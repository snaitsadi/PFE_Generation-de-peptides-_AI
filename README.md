# PFE_peptides

# Activer l'environnemen virtuelle (venv)
source venv/bin/activate

# Entraînez les modèles
python train_models.py

# Lancez le pipeline
pip install plotly
python run_pipeline.py --baseline --plot


# Visualisez les résultats avec Streamlit

pip install streamlit


streamlit run demo.py


streamlit run demo.py --server.fileWatcherType none