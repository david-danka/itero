import os

import pytest

from itero import cli as cli_module
from itero.cli import build_parser, cli
from itero.exceptions import InvalidNumSidesError


# ---------------------------------------------------------------------------
# Argument parsing (no mocking needed — build_parser() is pure)
# ---------------------------------------------------------------------------

def test_defaults():
    args = build_parser().parse_args([])

    assert args.num_sides == 5
    assert args.iterations is None
    assert args.ratio == 0.2
    assert args.cmap is None
    assert args.color is None
    assert args.alpha == 1.0
    assert args.figure_size == [8, 8]
    assert args.save_path is None
    assert args.no_show is False
    assert args.backend == "matplotlib"


def test_parses_all_flags():
    args = build_parser().parse_args([
        "--num-sides", "8",
        "--iterations", "50",
        "--ratio", "0.3",
        "--cmap", "plasma",
        "--alpha", "0.5",
        "--figure-size", "4", "6",
        "--save-path", "out.png",
        "--no-show",
        "--backend", "plotly",
    ])

    assert args.num_sides == 8
    assert args.iterations == 50
    assert args.ratio == 0.3
    assert args.cmap == "plasma"
    assert args.alpha == 0.5
    assert args.figure_size == [4, 6]
    assert args.save_path == "out.png"
    assert args.no_show is True
    assert args.backend == "plotly"


def test_rejects_unknown_backend():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--backend", "bogus"])


# ---------------------------------------------------------------------------
# cli() cross-argument validation and exit-code mapping (plot_polygons mocked)
# ---------------------------------------------------------------------------

def test_no_show_without_save_path_errors(monkeypatch, capsys):
    monkeypatch.setattr(cli_module.sys, "argv", ["itero", "--no-show"])

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 2
    assert "--no-show requires --save-path" in capsys.readouterr().err


def test_cmap_and_color_together_errors(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_module.sys, "argv", ["itero", "--cmap", "viridis", "--color", "red"]
    )

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 2
    assert "not both" in capsys.readouterr().err


def test_num_sides_over_max_errors(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_module.sys, "argv",
        ["itero", "--num-sides", str(cli_module.MAX_SIDES + 1)],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 2
    assert "--num-sides" in capsys.readouterr().err


def test_iterations_over_max_errors(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_module.sys, "argv",
        ["itero", "--iterations", str(cli_module.MAX_ITERATIONS + 1)],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 2
    assert "--iterations" in capsys.readouterr().err


def test_auto_iterations_over_max_errors(monkeypatch, capsys):
    """Regression: omitting --iterations (the documented default --
    'computed automatically to fill the figure') used to bypass
    MAX_ITERATIONS entirely, since the CLI-side check only looked at an
    explicitly-passed args.iterations. A small --ratio combined with a
    large --num-sides made the auto-computed count blow up into the
    hundreds of millions with nothing to catch it."""
    monkeypatch.setattr(
        cli_module.sys, "argv",
        ["itero", "--num-sides", "1000", "--ratio", "0.001", "--no-show", "--save-path", "x.png"],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 1
    assert "Auto-computed iterations" in capsys.readouterr().err


@pytest.mark.parametrize("num_sides,ratio", [(0, 0.2), (1, 0.2), (2, 0.5)])
def test_num_sides_below_minimum_errors_cleanly_with_auto_iterations(num_sides, ratio, monkeypatch, capsys):
    """Regression: cli.py resolves the auto-computed iteration count
    (via resolve_iterations) before ever calling plot_polygons/
    Polygon.regular, which is the only thing that used to validate
    num_sides on this path. num_sides=0/1, or 2 at ratio=0.5, crashed
    with a raw, uncaught ZeroDivisionError or ValueError instead of the
    clean InvalidNumSidesError num_sides=2 at the default ratio already
    got (that one happened to reach Polygon.regular before any math
    degenerated)."""
    monkeypatch.setattr(
        cli_module.sys, "argv",
        [
            "itero", "--num-sides", str(num_sides), "--ratio", str(ratio),
            "--no-show", "--save-path", "x.png",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 1
    assert "num_sides must be greater than or equal to 3" in capsys.readouterr().err


def test_num_sides_at_max_is_allowed(monkeypatch):
    """MAX_SIDES itself must not be rejected -- only values strictly above
    it. --iterations is given explicitly here to isolate that from the
    separate auto-computed-iterations guardrail: at num_sides=MAX_SIDES,
    the default --ratio auto-computes well over MAX_ITERATIONS on its
    own, which is a real (and correct) rejection, just not the one this
    test is about."""
    calls = []
    monkeypatch.setattr(cli_module, "plot_polygons", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(
        cli_module.sys, "argv",
        [
            "itero", "--num-sides", str(cli_module.MAX_SIDES), "--iterations", "10",
            "--no-show", "--save-path", "x.png",
        ],
    )

    cli()

    assert len(calls) == 1


def test_polygon_iter_error_exits_1_with_clean_message(monkeypatch, capsys):
    def _raise(*args, **kwargs):
        raise InvalidNumSidesError("bad number of sides")

    monkeypatch.setattr(cli_module, "plot_polygons", _raise)
    monkeypatch.setattr(cli_module.sys, "argv", ["itero"])

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 1
    assert "Error: bad number of sides" in capsys.readouterr().err


def test_keyboard_interrupt_exits_130(monkeypatch, capsys):
    def _raise(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli_module, "plot_polygons", _raise)
    monkeypatch.setattr(cli_module.sys, "argv", ["itero"])

    with pytest.raises(SystemExit) as exc_info:
        cli()

    assert exc_info.value.code == 130
    assert "Aborted" in capsys.readouterr().err


def test_calls_plot_polygons_with_mapped_arguments(monkeypatch):
    calls = []

    def _record(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(cli_module, "plot_polygons", _record)
    monkeypatch.setattr(
        cli_module.sys, "argv",
        ["itero", "--num-sides", "7", "--no-show", "--save-path", "x.png", "--backend", "plotly"],
    )

    cli()

    assert len(calls) == 1
    call = calls[0]
    assert call["num_sides"] == 7
    assert call["show"] is False  # --no-show inverted
    assert call["save_path"] == "x.png"
    assert call["backend"] == "plotly"


# ---------------------------------------------------------------------------
# End-to-end smoke tests (real pipeline, both backends)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("backend", ["matplotlib", "plotly"])
def test_end_to_end_smoke(monkeypatch, tmp_path, backend):
    if backend == "plotly":
        pytest.importorskip("kaleido")
    out = tmp_path / f"smoke_{backend}.png"
    monkeypatch.setattr(
        cli_module.sys, "argv",
        [
            "itero", "--num-sides", "6", "--ratio", "0.15",
            "--no-show", "--save-path", str(out), "--backend", backend,
        ],
    )

    cli()

    assert out.exists()
    assert out.stat().st_size > 0
