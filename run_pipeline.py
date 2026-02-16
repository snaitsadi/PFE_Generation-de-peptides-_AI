#!/usr/bin/env python3
import yaml
import json
import matplotlib.pyplot as plt
import seaborn as sns
from orchestrator import Orchestrator
from evaluation import Evaluator
from baseline import run_baseline
import argparse

def plot_evolution(metrics: dict, save_path: str = None):
    """Visualise l'évolution des scores"""
    evolution = metrics.get('evolution', {})
    
    if not evolution:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # 1. Évolution de la validité
    axes[0, 0].plot(evolution['iterations'], evolution['valid_counts'], 
                    marker='o', linewidth=2)
    axes[0, 0].set_xlabel('Itération')
    axes[0, 0].set_ylabel('Nombre de peptides valides')
    axes[0, 0].set_title('Évolution de la validité')
    axes[0, 0].grid(True, alpha=0.3)