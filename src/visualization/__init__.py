"""
Módulo para geração e controle estético de visualizações gráficas.
"""
from .plots import (
    set_chart_style,
    plot_temporal_trend,
    plot_top_municipalities,
    plot_monthly_heatmap
)

__all__ = [
    "set_chart_style",
    "plot_temporal_trend",
    "plot_top_municipalities",
    "plot_monthly_heatmap"
]
