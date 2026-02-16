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



    # 2. Évolution des scores
    axes[0, 1].plot(evolution['iterations'], evolution['avg_activity'], 
                    label='Activité', marker='s')
    axes[0, 1].plot(evolution['iterations'], evolution['avg_toxicity'], 
                    label='Toxicité', marker='^')
    axes[0, 1].plot(evolution['iterations'], evolution['avg_composite'], 
                    label='Composite', marker='d', linewidth=2)
    axes[0, 1].set_xlabel('Itération')
    axes[0, 1].set_ylabel('Score')
    axes[0, 1].set_title('Évolution des scores')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    

    # 3. Taux de passage par contrainte (bar chart)
    pass_rates = metrics.get('final_constraint_pass_rate', {})
    if pass_rates:
        constraints = list(pass_rates.keys())
        rates = list(pass_rates.values())
        axes[1, 0].bar(constraints, rates, color='skyblue')
        axes[1, 0].set_xlabel('Contrainte')
        axes[1, 0].set_ylabel('Taux de passage')
        axes[1, 0].set_title('Taux de passage par contrainte (final)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        for i, v in enumerate(rates):
            axes[1, 0].text(i, v + 0.01, f'{v:.1%}', 
                           ha='center', va='bottom')
            


    # 4. Diversité (box plot des distances)
    diversity = metrics.get('final_diversity', {})
    if diversity:
        axes[1, 1].text(0.5, 0.5, 
                       f"Diversité:\n"
                       f"Distance moyenne: {diversity.get('levenshtein_mean', 0):.1f}\n"
                       f"Séquences uniques: {diversity.get('unique_count', 0)}\n"
                       f"Ratio unique: {diversity.get('unique_ratio', 0):.1%}\n"
                       f"Entropie: {diversity.get('shannon_entropy', 0):.2f}",
                       transform=axes[1, 1].transAxes,
                       ha='center', va='center',
                       fontsize=12,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        axes[1, 1].axis('off')
        axes[1, 1].set_title('Métriques de diversité')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Graphique sauvegardé : {save_path}")
    
    plt.show()



def main():
    parser = argparse.ArgumentParser(description='Pipeline agentique pour la génération de peptides')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Chemin vers le fichier de configuration')
    parser.add_argument('--baseline', action='store_true',
                       help='Exécuter aussi la baseline')
    parser.add_argument('--plot', action='store_true',
                       help='Générer les graphiques')
    args = parser.parse_args()
    
    # 1. Exécuter le pipeline
    print("=== Exécution du pipeline agentique ===")
    orchestrator = Orchestrator(config_path=args.config)
    pipeline_logs = orchestrator.run()
    
    # 2. Évaluer les résultats
    evaluator = Evaluator()
    pipeline_metrics = evaluator.evaluate_pipeline(
        pipeline_logs, orchestrator.chemistry
    )