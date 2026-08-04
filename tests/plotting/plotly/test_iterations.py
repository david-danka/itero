from itero.plotting._plotly._iterations import plotly_eps_over_r


def test_matches_manual_calculation():
    figure_width, figure_height, linewidth = 8.0, 8.0, 1.5

    result = plotly_eps_over_r(figure_width, figure_height, linewidth)

    lw_inches = linewidth / 72
    expected = lw_inches / min(figure_width, figure_height)

    assert result == expected


def test_larger_figure_gives_smaller_threshold():
    small = plotly_eps_over_r(2, 2)
    large = plotly_eps_over_r(20, 20)

    assert large < small


def test_larger_linewidth_gives_larger_threshold():
    thin = plotly_eps_over_r(8, 8, linewidth=0.5)
    thick = plotly_eps_over_r(8, 8, linewidth=5.0)

    assert thick > thin
