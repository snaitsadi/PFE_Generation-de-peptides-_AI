import numpy as np
import typing import List, Tuple 
import random 
from utils import AMINO8ACIDS, generate_random_peptide 


class designerAgent:
    def __init__(self, min_length: int = 5, max_length: int = 50):
        self.min_length = min_length
        self.max_length = max_length

    def generate_initial_population(self, size: int = 100) -> List[str]:
        """Génère une population initiale de peptides"""
        return [generate_random_peptide(self.min_length, self.max_length)
                for _ in range(size)] 
    
    def mutate(self, peptide: str, mutation_rate: float = 0.1) -> str:
        """Applique une mutation aléatoire"""
        peptide_list = list(peptide)
        for i in range(len(peptide_list)):
            if random.random() < mutation_rate:
                peptide_list[i] = random.choice(AMINO_ACIDS)
        return ''.join(peptide_list)
    

    def crossover(self, parent1: str, parent2: str) -> Tuple[str, str]:
        """Croisement à un point"""
        if len(parent1) < 2 or len(parent2) < 2:
            return parent1, parent2
        
        
                # Point de croisement aléatoire
        point1 = random.randint(1, len(parent1) - 1)
        point2 = random.randint(1, len(parent2) - 1)

        child1 = parent1[:point1] + parent2[point2:]
        child2 = parent2[:point2] + parent1[point1:]

        return child1, child2

    def generate_variants(self, peptides: List[str], 
                         mutation_rate: float = 0.1,
                         crossover_rate: float = 0.3,
                         elite_size: int = 5) -> List[str]:
        """Génère de nouvelles variantes à partir des meilleurs peptides"""
        new_population = []
