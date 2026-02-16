import numpy as np
from typing import Dict, List
from agents.designer import DesignerAgent
from agents.chemistry import ChemistryAgent
from agents.bio import BioAgent
from utils import generate_random_peptide

def run_baseline(population_size: int = 100, 
                num_iterations: int = 10,
                top_k: int = 10) -> Dict:
    """Exécute une baseline sans agents (génération aléatoire)"""
    
    designer = DesignerAgent()
    chemistry = ChemistryAgent()
    bio = BioAgent()
    
    logs = {
        'config': {
            'population_size': population_size,
            'num_iterations': num_iterations,
            'top_k': top_k,
            'method': 'random_baseline'
        },
        'iterations': []
    }
    
    all_peptides = []
    all_scores = []
    
    for iteration in range(num_iterations):
        # Génération aléatoire
        population = [generate_random_peptide(5, 50) 
                     for _ in range(population_size)]
        
        # Filtrage chimique
        valid_peptides = []
        for peptide in population:
            if chemistry.evaluate_all(peptide)['all_passed']:
                valid_peptides.append(peptide)
        
        # Évaluation biologique
        scores = []
        for peptide in valid_peptides:
            evaluation = bio.evaluate(peptide)
            scores.append({
                'peptide': peptide,
                'activity_score': evaluation['activity_score'],
                'toxicity_score': evaluation['toxicity_score'],
                'composite_score': evaluation['composite_score']
            })
        
        # Trier par score
        scores.sort(key=lambda x: x['composite_score'], reverse=True)

        # Log de l'itération (AVEC les moyennes d'activité et toxicité)
        iteration_log = {
            'iteration': iteration,
            'population_size': len(population),
            'valid_count': len(valid_peptides),
            'avg_activity': np.mean([s['activity_score'] for s in scores]) if scores else 0,
            'avg_toxicity': np.mean([s['toxicity_score'] for s in scores]) if scores else 0,
            'avg_composite': np.mean([s['composite_score'] for s in scores]) if scores else 0,
            'top_scores': scores[:top_k]
        }
        
        logs['iterations'].append(iteration_log)
        
        # Accumuler les meilleurs
        all_peptides.extend([s['peptide'] for s in scores[:top_k]])
        all_scores.extend(scores[:top_k])
    
    # Résultats finaux
    all_scores.sort(key=lambda x: x['composite_score'], reverse=True)
    logs['final_results'] = {
        'top_peptides': all_scores[:top_k],
        'best_peptide': all_scores[0] if all_scores else None
    }
    
    return logs