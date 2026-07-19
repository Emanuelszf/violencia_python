"""
Módulo de treinamento e avaliação de modelos.
"""
from .train_model import train_baseline_poisson, train_ml_model
from .evaluate_model import evaluate_predictions, evaluate_spatial_autocorrelation

__all__ = [
    "train_baseline_poisson",
    "train_ml_model",
    "evaluate_predictions",
    "evaluate_spatial_autocorrelation"
]
