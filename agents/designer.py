import numpy as np
import typing import List, Tuple 
import random 
from utils import AMINO8ACIDS, generate_random_peptide 


class designerAgent:
    def __init__(self, min_length: int = 5, max_length: int = 50):
        self.min_length = min_length
        self.max_length = max_length