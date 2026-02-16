import numpy as np
from typing import *

from utils import levenshtein_distance

class Evaluator:
    @staticmethod
    def calculate_validity(peptides: List[str], chemistry_agent) -> float:
        """Calcule le pourcentage de peptides valides"""
        if not peptides:
            return 0.0
        valid_count = sum(1 for p in peptides 
                         if chemistry_agent.evaluate_all(p)['all_passed'])
        return valid_count / len(peptides)
    

    @staticmethod
    def calculate_diversity(peptides: List[str]) -> Dict[str, float]:
        """Calcule diverses métriques de diversité"""
        if len(peptides) < 2:
            return {'levenshtein_mean': 0, 'unique_count': len(peptides)}
        
        # Distance de Levenshtein moyenne
        distances = []
        for i in range(len(peptides)):
            for j in range(i+1, len(peptides)):
                distances.append(levenshtein_distance(peptides[i], peptides[j]))
        
        # Nombre de peptides uniques
        unique_peptides = set(peptides)
        

        # Entropie de Shannon des acides aminés
        all_aas = ''.join(peptides)
        if all_aas:
            aa_counts = {aa: all_aas.count(aa) for aa in set(all_aas)}
            total = len(all_aas)
            entropy = -sum((count/total) * np.log2(count/total) 
                          for count in aa_counts.values())
        else:
            entropy = 0
        
        return {
            'levenshtein_mean': np.mean(distances) if distances else 0,
            'levenshtein_std': np.std(distances) if distances else 0,
            'unique_count': len(unique_peptides),
            'unique_ratio': len(unique_peptides) / len(peptides),
            'shannon_entropy': entropy
        }
    

    @staticmethod
    def calculate_constraint_pass_rate(peptides: List[str], chemistry_agent) -> Dict[str, float]:
        """Calcule le taux de passage par contrainte"""
        if not peptides:
            return {}
        
        constraints = ['length', 'charge', 'gravy', 'forbidden_patterns', 'solubility']
        pass_counts = {constraint: 0 for constraint in constraints}
        
        for peptide in peptides:
            results = chemistry_agent.evaluate_all(peptide)
            for constraint in constraints:
                if results.get(constraint, False):
                    pass_counts[constraint] += 1
        
        return {constraint: count/len(peptides) 
                for constraint, count in pass_counts.items()}
    

    @staticmethod
    def evaluate_pipeline(logs: Dict, chemistry_agent) -> Dict[str, Any]:
        """Évalue les performances du pipeline complet"""
        # Extraire les données des logs
        iterations = logs.get('iterations', [])
        final_results = logs.get('final_results', {})
        
        if not iterations:
            return {}
        
        # Évolution des scores
        evolution = {
            'iterations': [i['iteration'] for i in iterations],
            'valid_counts': [i['valid_count'] for i in iterations],
            'avg_activity': [i['avg_activity'] for i in iterations],
            'avg_toxicity': [i['avg_toxicity'] for i in iterations],
            'avg_composite': [i['avg_composite'] for i in iterations]
        }
        
        # Top peptides finaux
        top_peptides = [r['peptide'] for r in final_results.get('top_peptides', [])]
        
        # Calcul des métriques finales
        metrics = {
            'final_validity': Evaluator.calculate_validity(top_peptides, chemistry_agent),
            'final_diversity': Evaluator.calculate_diversity(top_peptides),
            'final_constraint_pass_rate': Evaluator.calculate_constraint_pass_rate(
                top_peptides, chemistry_agent
            ),
            'evolution': evolution,
            'top_peptides': final_results.get('top_peptides', [])
        }


        # Scores moyens du Top-K
        if metrics['top_peptides']:
            metrics['top_k_activity'] = np.mean([
                p['activity_score'] for p in metrics['top_peptides']
            ])
            metrics['top_k_toxicity'] = np.mean([
                p['toxicity_score'] for p in metrics['top_peptides']
            ])
            metrics['top_k_composite'] = np.mean([
                p['composite_score'] for p in metrics['top_peptides']
            ])
        
        return metrics
    
    @staticmethod
    def compare_with_baseline(pipeline_results: Dict, 
                            baseline_results: Dict) -> Dict[str, Any]:
        """Compare les résultats avec une baseline"""
        comparison = {}
        
        for metric in ['validity', 'activity_score', 'diversity', 'constraint_pass_rate']:
            if metric in pipeline_results and metric in baseline_results:
                pipeline_val = pipeline_results[metric]
                baseline_val = baseline_results[metric]
                
                if isinstance(pipeline_val, (int, float)) and isinstance(baseline_val, (int, float)):
                    improvement = ((pipeline_val - baseline_val) / baseline_val * 100 
                                 if baseline_val != 0 else float('inf'))
                    comparison[metric] = {
                        'pipeline': pipeline_val,
                        'baseline': baseline_val,
                        'improvement_percent': improvement
                    }
        
        return comparison