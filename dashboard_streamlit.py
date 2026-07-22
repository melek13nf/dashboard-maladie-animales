import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Maladies Animales",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📊 Dashboard des Actualités sur les Maladies Animales")
st.markdown("---")

@st.cache_data
def charger_donnees():
    """Charger les données avec cache"""
    try:
        df = pd.read_csv('dataset_maladies_animales_clean.csv')
        return df
    except:
        st.error("Erreur lors du chargement des données. Assurez-vous que le fichier dataset_maladies_animales_clean.csv existe.")
        return pd.DataFrame()

def main():
    # Charger les données
    df = charger_donnees()
    
    if df.empty:
        st.warning("Aucune donnée à afficher. Veuillez exécuter le script d'extraction et de nettoyage d'abord.")
        return
    
    # Sidebar avec filtres
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par langue
    langues = ['Toutes'] + sorted(df['langue'].unique().tolist())
    langue_selectionnee = st.sidebar.selectbox("Langue", langues)
    
    # Filtre par maladie
    maladies = ['Toutes'] + sorted(df['maladie'].unique().tolist())
    maladie_selectionnee = st.sidebar.selectbox("Maladie", maladies)
    
    # Filtre par source
    sources = ['Toutes'] + sorted(df['source_publication'].unique().tolist())
    source_selectionnee = st.sidebar.selectbox("Source", sources)
    
    # Appliquer les filtres
    df_filtre = df.copy()
    if langue_selectionnee != 'Toutes':
        df_filtre = df_filtre[df_filtre['langue'] == langue_selectionnee]
    if maladie_selectionnee != 'Toutes':
        df_filtre = df_filtre[df_filtre['maladie'] == maladie_selectionnee]
    if source_selectionnee != 'Toutes':
        df_filtre = df_filtre[df_filtre['source_publication'] == source_selectionnee]
    
    # Métriques principales
    st.subheader("📈 Métriques Globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Articles", len(df_filtre))
    
    with col2:
        mots_moyens = df_filtre['nombre_mots'].mean() if 'nombre_mots' in df_filtre.columns else 0
        st.metric("Mots Moyens par Article", f"{mots_moyens:.0f}")
    
    with col3:
        langues_uniques = df_filtre['langue'].nunique()
        st.metric("Langues Différentes", langues_uniques)
    
    with col4:
        maladies_uniques = df_filtre['maladie'].nunique()
        st.metric("Maladies Différentes", maladies_uniques)
    
    st.markdown("---")
    
    # Première ligne de graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution par langue
        if 'langue' in df_filtre.columns:
            fig_langue = px.pie(
                df_filtre, 
                names='langue', 
                title='Distribution par Langue',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_langue.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_langue, use_container_width=True)
    
    with col2:
        # Distribution par source
        if 'source_publication' in df_filtre.columns:
            source_counts = df_filtre['source_publication'].value_counts()
            fig_source = px.bar(
                x=source_counts.index,
                y=source_counts.values,
                title='Distribution par Source de Publication',
                labels={'x': 'Source', 'y': "Nombre d'articles"},
                color=source_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_source.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_source, use_container_width=True)
    
    # Deuxième ligne de graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Top des maladies
        if 'maladie' in df_filtre.columns:
            maladie_counts = df_filtre['maladie'].value_counts().head(10)
            fig_maladie = px.bar(
                x=maladie_counts.values,
                y=maladie_counts.index,
                orientation='h',
                title='Top 10 des Maladies',
                labels={'x': "Nombre d'articles", 'y': 'Maladie'},
                color=maladie_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_maladie, use_container_width=True)
    
    with col2:
        # Distribution de la longueur des articles
        if 'nombre_mots' in df_filtre.columns:
            fig_longueur = px.histogram(
                df_filtre,
                x='nombre_mots',
                title='Distribution du Nombre de Mots par Article',
                labels={'nombre_mots': 'Nombre de mots'},
                nbins=20,
                color_discrete_sequence=['#FF6B6B']
            )
            fig_longueur.update_layout(showlegend=False)
            st.plotly_chart(fig_longueur, use_container_width=True)
    
    # Troisième ligne - Cartes et analyses avancées
    st.subheader("🗺️ Analyse Géographique et Temporelle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution géographique
        if 'lieu' in df_filtre.columns:
            lieu_counts = df_filtre['lieu'].value_counts().head(8)
            fig_lieu = px.bar(
                x=lieu_counts.index,
                y=lieu_counts.values,
                title='Top 8 des Lieux Mentionnés',
                labels={'x': 'Lieu', 'y': "Nombre d'articles"},
                color=lieu_counts.values,
                color_continuous_scale='Greens'
            )
            fig_lieu.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_lieu, use_container_width=True)
    
    with col2:
        # Word cloud des maladies (simulé avec un bar chart)
        if 'maladie' in df_filtre.columns:
            all_maladies = ' '.join(df_filtre['maladie'].dropna().astype(str))
            maladies_par_mot = all_maladies.split()
            from collections import Counter
            word_freq = Counter(maladies_par_mot)
            
            top_words = dict(word_freq.most_common(15))
            fig_words = px.bar(
                x=list(top_words.values()),
                y=list(top_words.keys()),
                orientation='h',
                title='Mots Clés les Plus Fréquents (Maladies)',
                labels={'x': 'Fréquence', 'y': 'Mots'},
                color=list(top_words.values()),
                color_continuous_scale='Purples'
            )
            st.plotly_chart(fig_words, use_container_width=True)
    
    # Tableau des données détaillées
    st.subheader("📋 Données Détailées")
    
    # Sélection des colonnes à afficher
    colonnes_a_afficher = st.multiselect(
        "Colonnes à afficher:",
        options=df_filtre.columns.tolist(),
        default=['titre', 'langue', 'maladie', 'source_publication', 'date_publication', 'nombre_mots']
    )
    
    if colonnes_a_afficher:
        st.dataframe(
            df_filtre[colonnes_a_afficher],
            use_container_width=True,
            height=400
        )
    
    # Téléchargement des données filtrées
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Export des Données")
    
    csv = df_filtre.to_csv(index=False, encoding='utf-8')
    st.sidebar.download_button(
        label="Télécharger les données filtrées (CSV)",
        data=csv,
        file_name=f"maladies_animales_filtre_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()