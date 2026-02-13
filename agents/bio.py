import numpy as np
import joblib
from typing import Dict, List
from sklearn.preprocessing import StandardScaler
from utils import AMINO_ACIDS, calculate_charge, calculate_gravy 

class BioAgent:
    def __init__(self):
        self.activity_model = None
        self.toxicity_model = None
        self.scaler = None
        self.use_heuristic = True  # bascule automatique si modèles chargés

   
    #   Extraction des features 
  
    def extract_features(self, peptide: str) -> np.ndarray:
        features = []
        # 1. Longueur
        features.append(len(peptide))
        # 2. Charge nette
        features.append(calculate_charge(peptide))
        # 3. Hydrophobicité (GRAVY)
        features.append(calculate_gravy(peptide))
        # 4. Composition en acides aminés (20)
        aa_counts = {aa: peptide.count(aa) / len(peptide) if len(peptide) > 0 else 0 
                     for aa in AMINO_ACIDS}
        features.extend([aa_counts[aa] for aa in AMINO_ACIDS])
        # 5. Motifs simples
        motifs = ['RR', 'KK', 'WW', 'FF', 'LL', 'CC']
        features.extend([1 if motif in peptide else 0 for motif in motifs])
        return np.array(features).reshape(1, -1)
