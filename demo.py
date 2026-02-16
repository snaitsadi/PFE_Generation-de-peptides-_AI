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

            if baseline_metrics:
                baseline_constraints = baseline_metrics.get('final_constraint_pass_rate', {})
                fig.add_trace(go.Scatterpolar(
                    r=list(baseline_constraints.values()),
                    theta=list(baseline_constraints.keys()),
                    fill='toself',
                    name='Baseline'
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)

    elif section == " Évolution":
        evolution = pipeline_metrics.get('evolution', {})
        
        if evolution:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Validité par itération', 
                              'Scores par itération',
                              'Diversité',
                              'Comparaison des scores')
            )


            # Graphique 1: Validité
            fig.add_trace(
                go.Scatter(x=evolution['iterations'], 
                          y=evolution['valid_counts'],
                          mode='lines+markers',
                          name='Peptides valides'),
                row=1, col=1
            )
            
            # Graphique 2: Scores
            fig.add_trace(
                go.Scatter(x=evolution['iterations'], 
                          y=evolution['avg_activity'],
                          mode='lines+markers',
                          name='Activité'),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=evolution['iterations'], 
                          y=evolution['avg_toxicity'],
                          mode='lines+markers',
                          name='Toxicité'),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=evolution['iterations'], 
                          y=evolution['avg_composite'],
                          mode='lines+markers',
                          name='Composite',
                          line=dict(width=3)),
                row=1, col=2
            )


            # Graphique 3: Diversité (text)
            diversity = pipeline_metrics.get('final_diversity', {})
            diversity_text = (
                f"Distance de Levenshtein moyenne: {diversity.get('levenshtein_mean', 0):.1f}<br>"
                f"Écart-type: {diversity.get('levenshtein_std', 0):.1f}<br>"
                f"Séquences uniques: {diversity.get('unique_count', 0)}<br>"
                f"Ratio unique: {diversity.get('unique_ratio', 0):.1%}<br>"
                f"Entropie de Shannon: {diversity.get('shannon_entropy', 0):.2f}"
            )
            
            fig.add_annotation(
                text=diversity_text,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12),
                align="center",
                row=2, col=1
            )
            
            # Graphique 4: Comparaison finale
            if baseline_metrics:
                final_scores = {
                    'Pipeline': pipeline_metrics.get('top_k_composite', 0),
                    'Baseline': baseline_metrics.get('top_k_composite', 0)
                }
                
                fig.add_trace(
                    go.Bar(x=list(final_scores.keys()),
                          y=list(final_scores.values()),
                          name='Score composite final'),
                    row=2, col=2
                )
            
            fig.update_layout(height=800, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    elif section == " Top Peptides":
        top_peptides = pipeline_metrics.get('top_peptides', [])
        
        if top_peptides:
            # Convertir en DataFrame pour l'affichage
            df_data = []
            for i, peptide_data in enumerate(top_peptides, 1):
                df_data.append({
                    'Rang': i,
                    'Séquence': peptide_data['peptide'],
                    'Longueur': len(peptide_data['peptide']),
                    'Activité': f"{peptide_data['activity_score']:.3f}",
                    'Toxicité': f"{peptide_data['toxicity_score']:.3f}",
                    'Score Composite': f"{peptide_data['composite_score']:.3f}"
                })


            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Visualisation de la séquence du meilleur peptide
            if top_peptides:
                best = top_peptides[0]
                st.subheader(" Meilleur peptide")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Séquence", best['peptide'])
                with col2:
                    st.metric("Score d'activité", f"{best['activity_score']:.3f}")
                with col3:
                    st.metric("Score de toxicité", f"{best['toxicity_score']:.3f}")
                
                # Représentation colorée de la séquence
                st.subheader(" Représentation de la séquence")
                
                # Code couleur simple pour les acides aminés
                color_map = {
                    'A': '#FF6B6B', 'C': '#4ECDC4', 'D': '#FFD166', 
                    'E': '#06D6A0', 'F': '#118AB2', 'G': '#073B4C',
                    'H': '#EF476F', 'I': '#7209B7', 'K': '#3A86FF',
                    'L': '#8338EC', 'M': '#FB5607', 'N': '#FF006E',
                    'P': '#FFBE0B', 'Q': '#3A86FF', 'R': '#8338EC',
                    'S': '#06D6A0', 'T': '#118AB2', 'V': '#073B4C',
                    'W': '#EF476F', 'Y': '#7209B7'
                }
                
                html_str = "<div style='font-family: monospace; font-size: 18px;'>"
                for aa in best['peptide']:
                    color = color_map.get(aa, '#CCCCCC')
                    html_str += f"<span style='background-color: {color}; padding: 2px 4px; margin: 1px; border-radius: 3px;'>{aa}</span>"
                html_str += "</div>"
                
                st.markdown(html_str, unsafe_allow_html=True)

    elif section == "Comparaison Baseline":
        if not comparison:
            st.info("La baseline n'a pas été exécutée. Exécutez avec '--baseline' pour voir la comparaison.")
            return
        
        st.subheader("Comparaison Pipeline vs Baseline")
        
        comparison_data = []
        for metric, values in comparison.items():
            if isinstance(values, dict) and 'improvement_percent' in values:
                comparison_data.append({
                    'Métrique': metric.replace('_', ' ').title(),
                    'Pipeline': values['pipeline'],
                    'Baseline': values['baseline'],
                    'Amélioration': f"{values['improvement_percent']:.1f}%"
                })


        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
            
            # Graphique de comparaison
            fig = go.Figure()
            
            for _, row in df_comparison.iterrows():
                fig.add_trace(go.Bar(
                    name=row['Métrique'],
                    x=['Pipeline', 'Baseline'],
                    y=[row['Pipeline'], row['Baseline']],
                    text=[f"{row['Pipeline']:.3f}", f"{row['Baseline']:.3f}"],
                    textposition='auto',
                ))
            
            fig.update_layout(
                barmode='group',
                title="Comparaison des métriques",
                yaxis_title="Valeur"
            )
            
            st.plotly_chart(fig, use_container_width=True)


    elif section == "Logs détaillés":
        st.subheader("Logs d'exécution")
        
        # Charger les logs complets
        try:
            with open('logs/pipeline_latest.json', 'r') as f:
                full_logs = json.load(f)
            
            # Afficher par itération
            iterations = full_logs.get('iterations', [])
            
            for i, iteration in enumerate(iterations):
                with st.expander(f"Itération {i}", expanded=(i == 0)):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Population totale:** {iteration['population_size']}")
                        st.write(f"**Peptides valides:** {iteration['valid_count']}")
                        st.write(f"**Score composite moyen:** {iteration['avg_composite']:.3f}")
                    
                    with col2:
                        st.write(f"**Score activité moyen:** {iteration['avg_activity']:.3f}")
                        st.write(f"**Score toxicité moyen:** {iteration['avg_toxicity']:.3f}")
                    
                    # Afficher les top peptides de cette itération
                    if 'top_scores' in iteration:
                        st.write("**Top peptides de cette itération:**")
                        for j, top_pep in enumerate(iteration['top_scores'][:3], 1):
                            st.code(f"{j}. {top_pep['peptide']} (score: {top_pep['composite']:.3f})")
        except FileNotFoundError:
            st.warning("Fichier de logs non trouvé")

if __name__ == '__main__':
    main()