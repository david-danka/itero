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
