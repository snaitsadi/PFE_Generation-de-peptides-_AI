import re

from typing import List, Dict, Tuple, Any
from utils import calculate_charge, calculate_gravy


class ChemistryAgent:
    def __init__(self, 
                 charge_range: List[float] = [-3, 3],
                 gravy_range: List[float] = [-2, 2],
                 forbidden_patterns: List[str] = None):
        
        self.charge_range = charge_range
        self.gravy_range = gravy_range
        self.forbidden_patterns = forbidden_patterns or ["CCC", "PPP", "KKKK"]


    def check_length(self, peptide: str, min_len: int = 5, max_len: int = 50) -> bool:
        """Vérifie la longueur du peptide"""
        return min_len <= len(peptide) <= max_len
    def check_charge(self, peptide: str) -> bool:
        """Vérifie la charge nette"""
        charge = calculate_charge(peptide)
        return self.charge_range[0] <= charge <= self.charge_range[1]
    

    def check_gravy(self, peptide: str) -> bool:
        """Vérifie l'hydrophobicité (GRAVY)"""
        gravy = calculate_gravy(peptide)
        return self.gravy_range[0] <= gravy <= self.gravy_range[1]
    
    def check_forbidden_patterns(self, peptide: str) -> bool:
        """Vérifie l'absence de motifs interdits"""
        for pattern in self.forbidden_patterns:
            if re.search(pattern, peptide):
                return False
        return True
    
    def check_solubility(self, peptide: str) -> bool:
        """Règle heuristique pour la solubilité proxy"""
        charge = calculate_charge(peptide)
        gravy = calculate_gravy(peptide)

        # Règle simple : bonne solubilité si charge > -2 et GRAVY < 1
        return charge > -2 and gravy < 1
    


    def evaluate_all(self, peptide: str) -> Dict[str, bool]:
        """Évalue toutes les contraintes chimiques"""
        return {
            'length': self.check_length(peptide),
            'charge': self.check_charge(peptide),
            'gravy': self.check_gravy(peptide),
            'forbidden_patterns': self.check_forbidden_patterns(peptide),
            'solubility': self.check_solubility(peptide),
            'all_passed': all([
                self.check_length(peptide),
                self.check_charge(peptide),
                self.check_gravy(peptide),
                self.check_forbidden_patterns(peptide),
                self.check_solubility(peptide)
            ])
        }
    

    def filter_population(self, peptides: List[str]) -> Tuple[List[str], List[Dict]]:
        """Filtre une population de peptides selon les contraintes"""
        valid_peptides = []
        validation_results = []
        
        for peptide in peptides:
            results = self.evaluate_all(peptide)
            validation_results.append({
                'peptide': peptide,
                **results
            })
            if results['all_passed']:
                valid_peptides.append(peptide)
        
        return valid_peptides, validation_results