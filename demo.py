#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

def load_results():
    """Charge les résultats depuis le fichier JSON"""
    try:
        with open('results/final_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("Veuillez d'abord exécuter le pipeline avec 'python run_pipeline.py'")
        return None
    
def main():
    st.set_page_config(page_title="Pipeline Agentique - Génération de Peptides", 
                      layout="wide")
    
    st.title("Pipeline Agentique pour la Génération de Peptides")


    results = load_results()
    if not results:
        return

    pipeline_metrics = results.get('pipeline_metrics', {})
    baseline_metrics = results.get('baseline_metrics', {})
    comparison = results.get('comparison', {})
    

    # Sidebar
    st.sidebar.header("Navigation")
    section = st.sidebar.radio(
        "Sélectionnez une section:",
        [" Vue d'ensemble", " Évolution", " Top Peptides", 
         " Comparaison Baseline", " Logs détaillés"]
    )


    if section == " Vue d'ensemble":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Validité finale",
                value=f"{pipeline_metrics.get('final_validity', 0):.1%}",
                delta=f"{comparison.get('validity', {}).get('improvement_percent', 0):.1f}%" 
                if comparison else None
            )


        with col2:
            st.metric(
                label="Score composite (Top-K)",
                value=f"{pipeline_metrics.get('top_k_composite', 0):.3f}",
                delta=f"{comparison.get('activity_score', {}).get('improvement_percent', 0):.1f}%" 
                if comparison else None
            )
        
        with col3:
            diversity = pipeline_metrics.get('final_diversity', {})
            st.metric(
                label="Séquences uniques",
                value=diversity.get('unique_count', 0),
                delta=f"{diversity.get('unique_ratio', 0):.1%}"
            )
            

        # Graphique radar des contraintes
        st.subheader(" Taux de passage par contrainte")
        constraints = pipeline_metrics.get('final_constraint_pass_rate', {})
        
        if constraints:
            fig = go.Figure(data=go.Scatterpolar(
                r=list(constraints.values()),
                theta=list(constraints.keys()),
                fill='toself',
                name='Pipeline'
            ))