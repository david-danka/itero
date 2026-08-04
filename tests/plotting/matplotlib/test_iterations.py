import matplotlib.pyplot as plt

from itero.plotting._matplotlib._iterations import matplotlib_eps_over_r


def test_matches_manual_calculation():
    figure_width, figure_height, dpi, linewidth = 8.0, 8.0, 100.0, 1.5

    result = matplotlib_eps_over_r(figure_width, figure_height, dpi, linewidth)

    width = figure_width * dpi
    height = figure_height * dpi
    axes_width_fraction = (
        plt.rcParams["figure.subplot.right"] - plt.rcParams["figure.subplot.left"]
    )
    axes_height_fraction = (
        plt.rcParams["figure.subplot.top"] - plt.rcParams["figure.subplot.bottom"]
    )
    axes_width = width * axes_width_fraction
    axes_height = height * axes_height_fraction
    lw_pixels = linewidth / 72 * dpi
    eps_pixels = lw_pixels / 2
    expected = eps_pixels * 2 / min(axes_height, axes_width)

    assert result == expected


def test_larger_figure_gives_smaller_threshold():
    small = matplotlib_eps_over_r(2, 2)
    large = matplotlib_eps_over_r(20, 20)

    assert large < small


def test_larger_linewidth_gives_larger_threshold():
    thin = matplotlib_eps_over_r(8, 8, linewidth=0.5)
    thick = matplotlib_eps_over_r(8, 8, linewidth=5.0)

    assert thick > thin
