import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import json
from datetime import datetime

# Alphabet des acides aminés standards (20)
AMINO_ACIDS = 'ACDEFGHIKLMNPQRSTVWY'

def generate_random_peptide(min_len: int = 5, max_len: int = 50) -> str:
    """Génère un peptide aléatoire"""
    length = np.random.randint(min_len, max_len + 1)
    return ''.join(np.random.choice(list(AMINO_ACIDS), length))

def calculate_charge(peptide: str) -> float:
    """Calcule la charge nette à pH 7"""
    charge_table = {
        'D': -1, 'E': -1,  # Acides
        'K': 1, 'R': 1, 'H': 0.1,  # Basiques (H partiellement chargé)
        # Autres: neutres
    }
    return sum(charge_table.get(aa, 0) for aa in peptide)


def calculate_gravy(peptide: str) -> float:
    """Calcule l'index GRAVY (hydrophobicité)"""
    # Valeurs Kyte-Doolittle simplifiées
    gravy_table = {
        'A': 1.8, 'C': 2.5, 'D': -3.5, 'E': -3.5, 'F': 2.8,
        'G': -0.4, 'H': -3.2, 'I': 4.5, 'K': -3.9, 'L': 3.8,
        'M': 1.9, 'N': -3.5, 'P': -1.6, 'Q': -3.5, 'R': -4.5,
        'S': -0.8, 'T': -0.7, 'V': 4.2, 'W': -0.9, 'Y': -1.3
    }
    if len(peptide) == 0:
        return 0
    return sum(gravy_table.get(aa, 0) for aa in peptide) / len(peptide)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Distance de Levenshtein entre deux séquences"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def save_logs(iteration_data: Dict, filename: str = None):
    """Sauvegarde les logs d'itération"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/pipeline_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(iteration_data, f, indent=2)