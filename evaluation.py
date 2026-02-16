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
        