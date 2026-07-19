"""
Módulo para geração e controle estético de visualizações gráficas de alta qualidade.
"""
from .plots import (
    set_chart_style,
    plot_temporal_trend,
    plot_top_municipalities,
    plot_planning_regions,
    plot_regional_facet_trends,
    plot_rmf_vs_interior_trend,
    plot_crime_nature_breakdown,
    plot_victim_demographics,
    plot_monthly_heatmap,
    plot_seasonality_bars
)

__all__ = [
    "set_chart_style",
    "plot_temporal_trend",
    "plot_top_municipalities",
    "plot_planning_regions",
    "plot_regional_facet_trends",
    "plot_rmf_vs_interior_trend",
    "plot_crime_nature_breakdown",
    "plot_victim_demographics",
    "plot_monthly_heatmap",
    "plot_seasonality_bars"
]
