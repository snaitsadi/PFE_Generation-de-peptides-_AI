import yaml
import json
import numpy as np

from typing import List, Dict, Any
from tqdm import tqdm
from agents.designer import DesignerAgent
from agents.chemistry import ChemistryAgent
from agents.bio import BioAgent
from utils import save_logs

class Orchestrator:
    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser les agents
        self.designer = DesignerAgent(
            min_length=self.config['pipeline']['min_length'],
            max_length=self.config['pipeline']['max_length']
        )
        
        self.chemistry = ChemistryAgent(
            charge_range=self.config['chemistry']['charge_range'],
            gravy_range=self.config['chemistry']['gravy_range'],
            forbidden_patterns=self.config['chemistry']['forbidden_patterns']
        )
        
        self.bio = BioAgent()
        
        # Paramètres du pipeline
        try:
            act_path = self.config['bio']['activity_model_path']
            tox_path = self.config['bio']['toxicity_model_path']
            scaler_path = self.config['bio'].get('scaler_path', None)
            self.bio.load_models(act_path, tox_path, scaler_path)
        except KeyError:
            print("ℹ  Aucun chemin de modèle spécifié, utilisation des heuristiques.")