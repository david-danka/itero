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
