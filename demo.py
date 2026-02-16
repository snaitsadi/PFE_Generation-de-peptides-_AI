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
