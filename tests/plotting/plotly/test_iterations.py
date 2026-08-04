from itero.plotting._plotly._iterations import plotly_eps_over_r


def test_matches_manual_calculation():
    figure_width, figure_height, dpi, linewidth = 8.0, 8.0, 100.0, 1.5

    result = plotly_eps_over_r(figure_width, figure_height, dpi, linewidth)

    width = figure_width * dpi
    height = figure_height * dpi
    lw_pixels = linewidth / 72 * dpi
    eps_pixels = lw_pixels / 2
    expected = eps_pixels * 2 / min(width, height)

    assert result == expected


def test_larger_figure_gives_smaller_threshold():
    small = plotly_eps_over_r(2, 2)
    large = plotly_eps_over_r(20, 20)

    assert large < small


def test_larger_linewidth_gives_larger_threshold():
    thin = plotly_eps_over_r(8, 8, linewidth=0.5)
    thick = plotly_eps_over_r(8, 8, linewidth=5.0)

    assert thick > thin
