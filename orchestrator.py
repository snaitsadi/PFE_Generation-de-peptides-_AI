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
            print("ℹ Aucun chemin de modèle spécifié, utilisation des heuristiques.")





        self.population_size = self.config['pipeline']['population_size']
        self.num_iterations = self.config['pipeline']['num_iterations']
        self.top_k = self.config['pipeline']['top_k']
        self.mutation_rate = self.config['pipeline']['mutation_rate']
        self.crossover_rate = self.config['pipeline']['crossover_rate']
        self.elite_size = self.config['pipeline']['elite_size']
        
        # Logs
        self.logs = {
            'config': self.config,
            'iterations': []
        }
    
    def run_iteration(self, iteration: int, population: List[str]) -> Dict[str, Any]:
        """Exécute une itération complète"""
        iteration_log = {
            'iteration': iteration,
            'population_size': len(population)
        }
        
        # Étape 1: Filtrage chimique
        valid_peptides, chem_results = self.chemistry.filter_population(population)
        iteration_log['valid_count'] = len(valid_peptides)
        iteration_log['chem_validation'] = chem_results[:5]  # Garder quelques exemples
        
        if len(valid_peptides) == 0:
            print(f"Attention: Aucun peptide valide à l'itération {iteration}")
            # Régénérer aléatoirement
            valid_peptides = self.designer.generate_initial_population(
                self.population_size // 2
            )
        
        # Étape 2: Évaluation biologique
        bio_results = self.bio.evaluate_population(valid_peptides)
        
        # Trier par score composite
        bio_results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        iteration_log['top_scores'] = [
            {
                'peptide': r['peptide'],
                'activity': r['activity_score'],
                'toxicity': r['toxicity_score'],
                'composite': r['composite_score']
            }
            for r in bio_results[:self.top_k]
        ]
        
        iteration_log['avg_activity'] = np.mean([r['activity_score'] for r in bio_results])
        iteration_log['avg_toxicity'] = np.mean([r['toxicity_score'] for r in bio_results])
        iteration_log['avg_composite'] = np.mean([r['composite_score'] for r in bio_results])


        # Sélectionner les meilleurs pour la prochaine génération
        top_peptides = [r['peptide'] for r in bio_results[:self.top_k * 2]]
        
        # Étape 3: Génération de nouvelles variantes
        if iteration < self.num_iterations - 1:
            new_population = self.designer.generate_variants(
                top_peptides,
                mutation_rate=self.mutation_rate,
                crossover_rate=self.crossover_rate,
                elite_size=self.elite_size
            )
            
            # Compléter avec des nouveaux aléatoires si nécessaire
            if len(new_population) < self.population_size:
                additional = self.designer.generate_initial_population(
                    self.population_size - len(new_population)
                )
                new_population.extend(additional)
        else:
            new_population = top_peptides[:self.population_size]
        
        iteration_log['next_population_size'] = len(new_population)
        
        return iteration_log, new_population, bio_results[:self.top_k]
    
    def run(self) -> Dict[str, Any]:
        """Exécute le pipeline complet"""
        print(f"Démarrage du pipeline avec {self.num_iterations} itérations...")
        
        # Population initiale
        population = self.designer.generate_initial_population(self.population_size)
        
        all_top_results = []
        
        for iteration in tqdm(range(self.num_iterations)):
            iteration_log, population, top_results = self.run_iteration(iteration, population)
            
            self.logs['iterations'].append(iteration_log)
            all_top_results.extend(top_results)
            
            print(f"\nItération {iteration}:")
            print(f"  Valides: {iteration_log['valid_count']}/{iteration_log['population_size']}")
            print(f"  Score composite moyen: {iteration_log['avg_composite']:.3f}")
            
            if iteration_log['top_scores']:
                best = iteration_log['top_scores'][0]
                print(f"  Meilleur: {best['peptide']} (score: {best['composite']:.3f})")
        
        # Résultats finaux
        self.logs['final_results'] = {
            'top_peptides': all_top_results[:self.top_k],
            'best_peptide': all_top_results[0] if all_top_results else None,
            'total_iterations': self.num_iterations
        }
        
        # Sauvegarder les logs
        save_logs(self.logs)
        
        return self.logs