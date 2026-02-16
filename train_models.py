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

df['SEQUENCE'] = df['SEQUENCE'].astype(str).str.upper().str.strip()
df = df[df['SEQUENCE'].apply(is_valid_sequence)]
df = df.drop_duplicates(subset='SEQUENCE')
print(f" Peptides uniques valides : {len(df)}")


# 2. Définition des labels


def is_antimicrobial(row):
    target = f"{row.get('TARGET GROUP', '')} {row.get('TARGET OBJECT', '')}"
    keywords = ['Gram+', 'Gram-', 'Gram positive', 'Gram negative']
    return 1 if any(kw in target for kw in keywords) else 0

def is_cytotoxic(row):
    target = f"{row.get('TARGET GROUP', '')} {row.get('TARGET OBJECT', '')}"
    # On considère toxique si la cible inclut des cellules de mammifère
    return 1 if 'Mammalian Cell' in target else 0

df['active'] = df.apply(is_antimicrobial, axis=1)
df['toxic'] = df.apply(is_cytotoxic, axis=1)

print(f"   - Actifs : {df['active'].sum()} ({df['active'].mean():.1%})")
print(f"   - Toxiques: {df['toxic'].sum()} ({df['toxic'].mean():.1%})")



# 3. Extraction des caractéristiques (features)

def extract_features(peptide):
    """Doit être IDENTIQUE à celle qui sera utilisée dans bio.py"""
    features = []
    # 1. Longueur
    features.append(len(peptide))
    # 2. Charge nette à pH 7
    features.append(calculate_charge(peptide))
    # 3. Hydrophobicité (GRAVY)
    features.append(calculate_gravy(peptide))
    # 4. Composition en acides aminés (20 fractions)
    aa_counts = {aa: peptide.count(aa) / len(peptide) for aa in AMINO_ACIDS}
    features.extend([aa_counts[aa] for aa in AMINO_ACIDS])
    # 5. Motifs simples (binaires)
    motifs = ['RR', 'KK', 'WW', 'FF', 'LL', 'CC']
    features.extend([1 if motif in peptide else 0 for motif in motifs])
    return np.array(features)

X = np.array([extract_features(seq) for seq in df['SEQUENCE']])
y_act = df['active'].values
y_tox = df['toxic'].values

print(f"   - Dimension des features : {X.shape[1]}")



# 4. Division entraînement / test

X_train, X_test, y_act_train, y_act_test = train_test_split(
    X, y_act, test_size=0.2, random_state=42, stratify=y_act
)
_, _, y_tox_train, y_tox_test = train_test_split(
    X, y_tox, test_size=0.2, random_state=42, stratify=y_tox
)


# 5. Normalisation

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# 6. Entraînement des modèles (Random Forest)

print("\n Entraînement du modèle d'activité...")
clf_act = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
clf_act.fit(X_train_scaled, y_act_train)
y_pred_act = clf_act.predict_proba(X_test_scaled)[:, 1]
auc_act = roc_auc_score(y_act_test, y_pred_act)
acc_act = accuracy_score(y_act_test, clf_act.predict(X_test_scaled))
print(f"   AUC  : {auc_act:.3f}")
print(f"   Acc  : {acc_act:.3f}")

print("\n Entraînement du modèle de toxicité...")
clf_tox = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
clf_tox.fit(X_train_scaled, y_tox_train)
y_pred_tox = clf_tox.predict_proba(X_test_scaled)[:, 1]
auc_tox = roc_auc_score(y_tox_test, y_pred_tox)
acc_tox = accuracy_score(y_tox_test, clf_tox.predict(X_test_scaled))
print(f"   AUC  : {auc_tox:.3f}")
print(f"   Acc  : {acc_tox:.3f}")


# 7. Sauvegarde des modèles et du scaler

os.makedirs('data/models', exist_ok=True)
joblib.dump(clf_act, 'data/models/activity_rf.pkl')
joblib.dump(clf_tox, 'data/models/toxicity_rf.pkl')
joblib.dump(scaler, 'data/models/scaler.pkl')
print("\n Modèles et scaler sauvegardés dans data/models/")