"""
Módulo de engenharia de atributos.
"""
from .build_features import (
    extract_temporal_features,
    create_age_groups,
    categorize_rmf_vs_interior,
    calculate_regional_metrics,
    validate_cvli_data,
    build_municipality_year_panel,
    add_fixed_periods,
    calculate_period_metrics,
    calculate_concentration_metrics,
    add_population_rates,
)

__all__ = [
    "extract_temporal_features",
    "create_age_groups",
    "categorize_rmf_vs_interior",
    "calculate_regional_metrics",
    "validate_cvli_data",
    "build_municipality_year_panel",
    "add_fixed_periods",
    "calculate_period_metrics",
    "calculate_concentration_metrics",
    "add_population_rates",
]
