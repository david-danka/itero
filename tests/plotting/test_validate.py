import pytest

from itero.exceptions import (
    InvalidAlphaError,
    InvalidColorSpecError,
    InvalidFigureSizeError,
    RenderingError,
)
from itero.plotting._validate import (
    validate_alpha,
    validate_color_spec,
    validate_figure_size,
    validate_save_path,
)


@pytest.mark.parametrize("figure_size", [(-1, 4), (4, -1), (0, 4), (4, 0), (0, 0)])
def test_rejects_non_positive_sizes(figure_size):
    with pytest.raises(InvalidFigureSizeError):
        validate_figure_size(figure_size)


@pytest.mark.parametrize("figure_size", [(1, 1), (8, 8), (0.1, 20)])
def test_accepts_positive_sizes(figure_size):
    validate_figure_size(figure_size)  # should not raise


@pytest.mark.parametrize("figure_size", [(float("nan"), 4), (4, float("nan"))])
def test_rejects_nan_size(figure_size):
    """Regression: a bare `<= 0` comparison silently let NaN through,
    since every comparison with NaN is False in Python."""
    with pytest.raises(InvalidFigureSizeError):
        validate_figure_size(figure_size)


def test_validate_save_path_rejects_non_string_type():
    with pytest.raises(RenderingError):
        validate_save_path(123)


def test_validate_save_path_rejects_missing_directory(tmp_path):
    with pytest.raises(RenderingError):
        validate_save_path(str(tmp_path / "missing" / "out.png"))


def test_validate_save_path_accepts_existing_directory(tmp_path):
    validate_save_path(str(tmp_path / "out.png"))  # should not raise


def test_validate_save_path_accepts_bare_filename(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    validate_save_path("out.png")  # dirname is "", falls back to "."


def test_validate_color_spec_rejects_both_given():
    with pytest.raises(InvalidColorSpecError):
        validate_color_spec("plasma", "red")


@pytest.mark.parametrize("cmap,color", [(None, None), ("plasma", None), (None, "red")])
def test_validate_color_spec_accepts_at_most_one(cmap, color):
    validate_color_spec(cmap, color)  # should not raise


@pytest.mark.parametrize("alpha", [-0.1, 1.1, float("nan"), "0.5", None])
def test_validate_alpha_rejects_invalid(alpha):
    with pytest.raises(InvalidAlphaError):
        validate_alpha(alpha)


@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.0])
def test_validate_alpha_accepts_valid(alpha):
    validate_alpha(alpha)  # should not raise
