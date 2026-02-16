# PFE_peptides

# Activer l'environnemen virtuelle (venv)
source venv/bin/activate

# Entraînez les modèles
python train_models.py

# Lancez le pipeline
python run_pipeline.py --baseline --plot

# Visualisez les résultats avec Streamlit
streamlit run demo.py