#!/usr/bin/env python3
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import sys
import os

sys.path.append(os.path.dirname(__file__))
from utils import AMINO_ACIDS, calculate_charge, calculate_gravy

# ------------------------------------------------------------
# 1. Chargement et nettoyage
# ------------------------------------------------------------
df = pd.read_csv('data/peptides.csv')

# Garder les séquences valides (uniquement 20 acides aminés standards)
valid_aas = set(AMINO_ACIDS)
def is_valid_sequence(seq):
    if pd.isna(seq):
        return False
    seq = str(seq).upper().strip()
    return all(aa in valid_aas for aa in seq) and len(seq) > 0