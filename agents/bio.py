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


    #   Chargement des modèles pré-entraînés

    def load_models(self, activity_path: str, toxicity_path: str, scaler_path: str = None):
        try:
            self.activity_model = joblib.load(activity_path)
            self.toxicity_model = joblib.load(toxicity_path)
            if scaler_path:
                self.scaler = joblib.load(scaler_path)
            else:
                    self.scaler = None
            self.use_heuristic = False
            print("Modèles bio chargés avec succès.")
        except Exception as e:
            print(f" Échec du chargement des modèles : {e}")
            print(" Utilisation des règles heuristiques par défaut.")
            self.use_heuristic = True

     #   Prédiction d'activité

    def predict_activity(self, peptide: str) -> float:
        if not self.use_heuristic and self.activity_model is not None:
            features = self.extract_features(peptide)
            if self.scaler:
                features = self.scaler.transform(features)
            proba = self.activity_model.predict_proba(features)[0, 1]
            return float(proba)
        else:
            # Règle heuristique simple (charge positive, hydrophobicité modérée)
            charge = calculate_charge(peptide)
            gravy = calculate_gravy(peptide)
            base_score = max(0, min(1, (charge + 3) / 6))
            penalty = abs(gravy) / 2
            return max(0, base_score - 0.3 * penalty)
    
    #  Prédiction de toxicité 

    def predict_toxicity(self, peptide: str) -> float:
        if not self.use_heuristic and self.toxicity_model is not None: 
            features = self.extract_features(peptide)
            if self.scaler:
                features = self.scaler.transform(features)
            proba = self.toxicity_model.predict_proba(features)[0, 1]
            return float(proba)
        else:
            #Régle heuristqiue : forte hydrophobicité - toxicité
            gravy = calculate_gravy(peptide)
            return min(1, max(0, (gravy + 2) / 4))