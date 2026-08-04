import pytest

from itero.exceptions import InvalidFigureSizeError
from itero.plotting._validate import validate_figure_size


@pytest.mark.parametrize("figure_size", [(-1, 4), (4, -1), (0, 4), (4, 0), (0, 0)])
def test_rejects_non_positive_sizes(figure_size):
    with pytest.raises(InvalidFigureSizeError):
        validate_figure_size(figure_size)


@pytest.mark.parametrize("figure_size", [(1, 1), (8, 8), (0.1, 20)])
def test_accepts_positive_sizes(figure_size):
    validate_figure_size(figure_size)  # should not raise
