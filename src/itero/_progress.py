"""Optional progress reporting for potentially slow operations.

Library code (core, plotting) never assumes a terminal exists, or that
anyone wants console output -- every function that can take a while
accepts an optional reporter, defaulting to a silent no-op. Direct
API/library callers (Streamlit, notebooks, tests, plot_polygons called
without a reporter) see zero behavior change unless they explicitly
opt in. cli.py is the only place that constructs a real, visible one.

Two kinds of "slow" get two different treatments, deliberately:
- Countable-step operations (iterate_polygon's loop, Plotly's
  per-polygon trace-building loop) get a real percentage + ETA, since
  the total is known up front.
- Opaque, single blocking calls (Matplotlib's savefig, Plotly's
  write_image/kaleido export) get a spinner + elapsed time only -- a
  percentage there would have to be faked, since there's no way to
  know how far along an opaque call is.

Both stay silent for the first second: most renders never take that
long, and flashing a bar/spinner for a fraction of a second is worse
than saying nothing at all.

Progress reporting is inherently best-effort: it must never be the
reason a render fails. sys.stderr can legitimately be None (e.g. a
windowed/noconsole-packaged app on Windows), so CLIProgressReporter
detects an unusable stream at construction and quietly disables
itself rather than raising the first time it tries to use it.
"""

import sys
import threading
import time
from contextlib import contextmanager


class NullProgressReporter:
    """Silent no-op reporter -- the default everywhere except cli.py."""

    def iteration_step(self, current: int, total: int) -> None:
        pass

    def render_step(self, current: int, total: int) -> None:
        pass

    @contextmanager
    def phase(self, label: str):
        yield


class _DelayedBar:
    """Tracks one delayed, rate-limited, percentage-based progress bar.

    Stays invisible until `delay` seconds have elapsed since the first
    step of the current run (detected by current == 1, since every
    loop this wraps starts counting from there). Redraws are throttled
    separately for interactive terminals (smooth, frequent) and
    non-interactive output (occasional plain lines, since \\r tricks
    just garble a piped/redirected/logged stream).

    is_tty is resolved once by the caller and passed in, rather than
    queried here on every step() call -- isatty() is a real syscall
    (~250ns measured), and step() runs once per iteration; for a large
    iteration count with a cheap per-iteration cost (small num_sides),
    querying it every time is measurable, avoidable overhead for an
    answer that can't change mid-run.
    """

    def __init__(self, label: str, stream, is_tty: bool, delay: float = 1.0, width: int = 30):
        self._label = label
        self._stream = stream
        self._is_tty = is_tty
        self._delay = delay
        self._width = width
        self._start: float | None = None
        self._shown = False
        self._last_draw = 0.0

    def step(self, current: int, total: int) -> None:
        now = time.perf_counter()
        if current <= 1:
            self._start = now
            self._shown = False
            self._last_draw = 0.0
        if self._start is None:
            self._start = now

        elapsed = now - self._start
        if not self._shown:
            if elapsed < self._delay:
                return
            self._shown = True

        min_interval = 0.1 if self._is_tty else 1.0
        finished = current >= total
        if not finished and now - self._last_draw < min_interval:
            return
        self._last_draw = now
        self._draw(current, total, elapsed)
        if finished and self._is_tty:
            print(file=self._stream)  # leave the completed bar in place

    def _draw(self, current: int, total: int, elapsed: float) -> None:
        frac = current / total if total else 1.0
        rate = current / elapsed if elapsed > 0 else 0.0
        eta = (total - current) / rate if rate > 0 else 0.0

        if self._is_tty:
            filled = int(self._width * frac)
            bar = "#" * filled + "-" * (self._width - filled)
            print(
                f"\r{self._label} [{bar}] {frac:.0%} ({current}/{total}, eta {eta:.0f}s)",
                end="", file=self._stream, flush=True,
            )
        else:
            print(
                f"{self._label}: {current}/{total} ({frac:.0%}, elapsed {elapsed:.0f}s)",
                file=self._stream, flush=True,
            )


class CLIProgressReporter:
    """Real terminal feedback: delayed bars for countable loops, a
    delayed spinner for opaque single calls. Writes to stderr, matching
    cli.py's own error output -- so a --save-path'd stdout, or a piped/
    redirected/logged run, never gets progress noise mixed into it.
    """

    def __init__(self, stream=None, delay: float = 1.0):
        self._stream = stream if stream is not None else sys.stderr
        # sys.stderr can be None (e.g. a windowed/noconsole-packaged
        # app on Windows) -- disable quietly rather than crash the
        # render this is only meant to report on, not gate.
        self._enabled = self._stream is not None
        self._delay = delay
        self._is_tty = self._safe_isatty()
        self._iteration_bar = _DelayedBar("Iterating", self._stream, self._is_tty, delay)
        self._render_bar = _DelayedBar("Rendering", self._stream, self._is_tty, delay)

    def _safe_isatty(self) -> bool:
        if not self._enabled:
            return False
        try:
            return bool(self._stream.isatty())
        except (AttributeError, ValueError, OSError):
            # A stream that exists but can't answer isatty() (e.g.
            # already closed) is treated as non-interactive -- the
            # safer of the two assumptions, since \r-based redraws
            # garble non-terminal output but plain lines are always
            # readable either way.
            return False

    def iteration_step(self, current: int, total: int) -> None:
        if self._enabled:
            self._iteration_bar.step(current, total)

    def render_step(self, current: int, total: int) -> None:
        if self._enabled:
            self._render_bar.step(current, total)

    @contextmanager
    def phase(self, label: str):
        if not self._enabled:
            yield
            return

        stop = threading.Event()
        thread = threading.Thread(target=self._spin, args=(label, stop), daemon=True)
        thread.start()
        try:
            yield
        finally:
            stop.set()
            thread.join()

    def _spin(self, label: str, stop: threading.Event) -> None:
        start = time.perf_counter()
        shown = False
        frames = "|/-\\"
        i = 0
        last_line = 0.0
        while not stop.is_set():
            elapsed = time.perf_counter() - start
            if not shown:
                if elapsed >= self._delay:
                    shown = True
                else:
                    stop.wait(0.05)
                    continue
            now = time.perf_counter()
            if self._is_tty:
                print(
                    f"\r{label} {frames[i % len(frames)]} ({now - start:.0f}s)",
                    end="", file=self._stream, flush=True,
                )
                i += 1
                stop.wait(0.1)
            else:
                if now - last_line >= 1.0:
                    print(f"{label} ({now - start:.0f}s elapsed)", file=self._stream, flush=True)
                    last_line = now
                stop.wait(0.2)
        if shown and self._is_tty:
            print(file=self._stream)
