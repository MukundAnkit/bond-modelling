"""Tests for the reusable plotting utilities."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from src.utils.plotting import (
    BOND_COLORS,
    DEFAULT_CONFIG,
    FigureConfig,
    figure,
    finish_plot,
    price_yield_curve,
    reference_line,
    set_theme,
    subplots,
)


class TestSetTheme:
    def test_applies_expected_rcparams(self):
        original_dpi = plt.rcParams["figure.dpi"]
        original_fontsize = plt.rcParams["font.size"]
        set_theme()
        assert plt.rcParams["figure.dpi"] == 120
        assert plt.rcParams["font.size"] == 10
        # Restore
        plt.rcParams["figure.dpi"] = original_dpi
        plt.rcParams["font.size"] = original_fontsize


class TestFigureFactories:
    def test_figure_returns_fig_ax(self):
        fig, ax = figure()
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_figure_default_figsize(self):
        fig, ax = figure()
        assert fig.get_size_inches().tolist() == [8.0, 4.0]
        plt.close(fig)

    def test_figure_custom_figsize(self):
        fig, ax = figure(figsize=(12, 6))
        assert fig.get_size_inches().tolist() == [12.0, 6.0]
        plt.close(fig)

    def test_subplots_returns_fig_axes(self):
        fig, axes = subplots(1, 2)
        assert isinstance(fig, plt.Figure)
        assert len(axes) == 2
        plt.close(fig)

    def test_subplots_default_figsize(self):
        fig, axes = subplots(1, 2)
        assert fig.get_size_inches().tolist() == [10.0, 4.0]
        plt.close(fig)


class TestFinishPlot:
    def test_applies_grid_and_tight_layout(self):
        fig, ax = figure()
        finish_plot(ax, legend=False)
        assert ax.get_xgridlines()[0].get_visible()
        plt.close(fig)

    def test_sets_labels(self):
        fig, ax = figure()
        finish_plot(ax, xlabel="X", ylabel="Y", legend=False)
        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        plt.close(fig)

    def test_sets_title(self):
        fig, ax = figure()
        finish_plot(ax, title="Test Title", legend=False)
        assert ax.get_title() == "Test Title"
        plt.close(fig)


class TestReferenceLine:
    def test_adds_axhline(self):
        fig, ax = figure()
        reference_line(ax, y=100)
        lines = ax.get_lines()
        assert len(lines) == 1
        data_y = lines[0].get_ydata()
        assert data_y[0] == 100.0
        plt.close(fig)


class TestPriceYieldCurve:
    def test_plots_line(self):
        fig, ax = figure()
        yields = np.linspace(0.01, 0.10, 50)
        prices = np.linspace(90, 110, 50)
        price_yield_curve(ax, yields, prices)
        lines = ax.get_lines()
        assert len(lines) == 1
        plt.close(fig)

    def test_default_color(self):
        fig, ax = figure()
        yields = np.linspace(0.01, 0.10, 50)
        prices = np.linspace(90, 110, 50)
        price_yield_curve(ax, yields, prices)
        assert ax.get_lines()[0].get_color() == BOND_COLORS["price_curve"]
        plt.close(fig)

    def test_custom_label(self):
        fig, ax = figure()
        yields = np.linspace(0.01, 0.10, 50)
        prices = np.linspace(90, 110, 50)
        price_yield_curve(ax, yields, prices, label="My Bond")
        assert ax.get_lines()[0].get_label() == "My Bond"
        plt.close(fig)


class TestColors:
    def test_contains_expected_keys(self):
        expected_keys = [
            "price_curve",
            "coupon_bar",
            "face_bar",
            "solver",
            "solver_error",
            "bisection",
            "zero_coupon",
            "reference",
        ]
        for key in expected_keys:
            assert key in BOND_COLORS

    def test_values_are_valid_hex_or_name(self):
        for _name, value in BOND_COLORS.items():
            assert isinstance(value, str)
            assert len(value) > 0


class TestFigureConfig:
    def test_default_values(self):
        config = FigureConfig()
        assert config.single_figsize == (8, 4)
        assert config.subplot_figsize == (10, 4)
        assert config.legend_fontsize == 9
        assert config.subplot_legend_fontsize == 8

    def test_custom_values(self):
        config = FigureConfig(
            single_figsize=(10, 5),
            subplot_figsize=(12, 5),
            legend_fontsize=11,
            subplot_legend_fontsize=10,
        )
        assert config.single_figsize == (10, 5)
        assert config.subplot_figsize == (12, 5)
        assert config.legend_fontsize == 11
        assert config.subplot_legend_fontsize == 10

    def test_module_default_available(self):
        assert DEFAULT_CONFIG.single_figsize == (8, 4)
