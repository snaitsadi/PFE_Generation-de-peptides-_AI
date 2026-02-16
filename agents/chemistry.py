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
    