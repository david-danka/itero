import io
import time

import pytest

from itero._progress import CLIProgressReporter, NullProgressReporter


class _FakeStream(io.StringIO):
    """A StringIO whose isatty() is controllable, to exercise both the
    interactive-terminal and piped/redirected code paths deterministically."""

    def __init__(self, is_tty: bool):
        super().__init__()
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


class _CountingStream(io.StringIO):
    """A StringIO that tracks how many times isatty() gets called."""

    def __init__(self):
        super().__init__()
        self.isatty_calls = 0

    def isatty(self) -> bool:
        self.isatty_calls += 1
        return True


class _BrokenIsattyStream(io.StringIO):
    """A stream whose isatty() raises, simulating an already-closed or
    otherwise unusable stream that still exists."""

    def isatty(self):
        raise ValueError("I/O operation on closed file")


class TestNullProgressReporter:
    def test_iteration_step_is_a_silent_no_op(self):
        NullProgressReporter().iteration_step(1, 100)  # should not raise, no output

    def test_render_step_is_a_silent_no_op(self):
        NullProgressReporter().render_step(1, 100)  # should not raise

    def test_phase_is_a_no_op_context_manager(self):
        with NullProgressReporter().phase("doing something"):
            pass  # should not raise, no output

    def test_phase_propagates_exceptions(self):
        with pytest.raises(ValueError):
            with NullProgressReporter().phase("doing something"):
                raise ValueError("boom")


class TestCLIProgressReporterBars:
    def test_stays_silent_before_the_delay(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=10.0)  # long delay, never trips

        for i in range(1, 11):
            reporter.iteration_step(i, 10)

        assert stream.getvalue() == ""

    def test_shows_output_after_the_delay_elapses(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=0.05)

        reporter.iteration_step(1, 100)
        time.sleep(0.1)
        reporter.iteration_step(2, 100)

        assert "Iterating" in stream.getvalue()

    def test_tty_output_uses_carriage_return(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=0.0)

        reporter.iteration_step(1, 10)

        assert "\r" in stream.getvalue()

    def test_non_tty_output_has_no_carriage_return(self):
        stream = _FakeStream(is_tty=False)
        reporter = CLIProgressReporter(stream=stream, delay=0.0)

        reporter.iteration_step(1, 10)

        assert "\r" not in stream.getvalue()
        assert "Iterating" in stream.getvalue()

    def test_iteration_and_render_bars_are_independent(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=0.0)

        reporter.iteration_step(1, 5)
        reporter.render_step(1, 5)

        output = stream.getvalue()
        assert "Iterating" in output
        assert "Rendering" in output

    def test_new_run_resets_bar_state(self):
        """current == 1 signals a fresh loop starting -- its delay timer
        must reset rather than reuse a previous run's elapsed time."""
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=0.05)

        reporter.iteration_step(1, 10)
        time.sleep(0.1)
        reporter.iteration_step(10, 10)  # finishes and completes the first run

        stream.truncate(0)
        stream.seek(0)

        reporter.iteration_step(1, 10)  # a new run -- should be silent again immediately

        assert stream.getvalue() == ""


class TestCLIProgressReporterPhase:
    def test_stays_silent_for_a_fast_operation(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=1.0)

        with reporter.phase("Saving..."):
            pass  # fast -- well under the delay

        assert stream.getvalue() == ""

    def test_shows_output_for_a_slow_operation(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=0.05)

        with reporter.phase("Saving..."):
            time.sleep(0.3)

        assert "Saving..." in stream.getvalue()

    def test_propagates_exceptions_and_still_stops_the_spinner_thread(self):
        stream = _FakeStream(is_tty=True)
        reporter = CLIProgressReporter(stream=stream, delay=0.05)

        with pytest.raises(ValueError):
            with reporter.phase("Saving..."):
                time.sleep(0.2)
                raise ValueError("boom")

        # phase()'s finally block joins the spinner thread before
        # returning, so nothing should still be writing to the stream
        # after the context manager has exited.
        length_after_exit = len(stream.getvalue())
        time.sleep(0.3)
        assert len(stream.getvalue()) == length_after_exit

    def test_non_tty_phase_output_has_no_spinner_characters(self):
        stream = _FakeStream(is_tty=False)
        reporter = CLIProgressReporter(stream=stream, delay=0.05)

        with reporter.phase("Saving..."):
            time.sleep(0.3)

        output = stream.getvalue()
        assert "Saving..." in output
        assert "\r" not in output


class TestCLIProgressReporterRobustness:
    """Progress reporting is best-effort: it must never be the reason a
    render fails, no matter what state the output stream is in."""

    def test_isatty_is_queried_once_not_per_step(self):
        """Regression: isatty() is a real syscall (~250ns measured); a
        large iteration count with a cheap per-iteration cost (small
        num_sides) used to pay that cost on every single step() call
        once the bar became visible, for an answer that can't change
        mid-run."""
        stream = _CountingStream()
        reporter = CLIProgressReporter(stream=stream, delay=0.0)

        for i in range(1, 100_001):
            reporter.iteration_step(i, 100_000)

        assert stream.isatty_calls == 1

    def test_none_stream_does_not_crash(self):
        """Regression: sys.stderr can legitimately be None (e.g. a
        windowed/noconsole-packaged app on Windows). CLIProgressReporter()
        (no explicit stream) resolves to sys.stderr internally -- if that's
        None, every call used to raise AttributeError the moment the delay
        elapsed, taking the whole render down with it."""
        reporter = CLIProgressReporter(stream=None, delay=0.0)

        reporter.iteration_step(1, 10)  # should not raise
        reporter.render_step(1, 10)  # should not raise
        with reporter.phase("Saving..."):  # should not raise
            pass

    def test_broken_isatty_degrades_to_non_interactive_rather_than_raising(self):
        stream = _BrokenIsattyStream()

        reporter = CLIProgressReporter(stream=stream, delay=0.0)
        reporter.iteration_step(1, 10)  # should not raise

        assert "\r" not in stream.getvalue()
        assert "Iterating" in stream.getvalue()
