import pandas as pd
import numpy as np
import re

def verifier_pretraitement(df):
    """Vérifier la qualité du nettoyage et prétraitement"""
    
    print("=== VÉRIFICATION DU PRÉTRAITEMENT ===")
    
    # 1. Vérifier les valeurs manquantes
    print("\n1. VALEURS MANQUANTES:")
    for colonne in df.columns:
        nb_manquants = df[colonne].isna().sum()
        pourcentage = (nb_manquants / len(df)) * 100
        print(f"  {colonne}: {nb_manquants} manquants ({pourcentage:.1f}%)")
    
    # 2. Vérifier les statistiques de base
    print("\n2. STATISTIQUES DES TEXTES:")
    if 'nombre_mots' in df.columns:
        print(f"  Mots - Moyenne: {df['nombre_mots'].mean():.0f}, Min: {df['nombre_mots'].min()}, Max: {df['nombre_mots'].max()}")
    if 'nombre_caracteres' in df.columns:
        print(f"  Caractères - Moyenne: {df['nombre_caracteres'].mean():.0f}, Min: {df['nombre_caracteres'].min()}, Max: {df['nombre_caracteres'].max()}")
    
    # 3. Vérifier la distribution des langues
    print("\n3. DISTRIBUTION DES LANGUES:")
    if 'langue' in df.columns:
        print(df['langue'].value_counts())
    
    # 4. Vérifier les dates
    print("\n4. FORMAT DES DATES:")
    if 'date_publication' in df.columns:
        dates_uniques = df['date_publication'].unique()
        print(f"  Formats de date trouvés: {dates_uniques[:10]}")  # Afficher les 10 premiers
    
    # 5. Vérifier la longueur des résumés
    print("\n5. LONGUEUR DES RÉSUMÉS:")
    resumes_colonnes = ['resume_50_mots', 'resume_100_mots', 'resume_150_mots']
    for col in resumes_colonnes:
        if col in df.columns:
            longueurs = df[col].str.split().str.len()
            print(f"  {col}: Moyenne {longueurs.mean():.1f} mots")
    
    # 6. Vérifier les doublons
    print("\n6. DOUBLONS:")
    doublons = df.duplicated(subset=['url']).sum()
    print(f"  URLs dupliquées: {doublons}")
    
    # 7. Vérifier la cohérence des maladies
    print("\n7. MALADIES IDENTIFIÉES:")
    if 'maladie' in df.columns:
        print(df['maladie'].value_counts().head(10))

def nettoyer_donnees(df):
    """Nettoyer et prétraiter les données"""
    
    print("\n=== NETTOYAGE EN COURS ===")
    
    # 1. Supprimer les doublons
    df_clean = df.drop_duplicates(subset=['url']).copy()
    print(f"Doublons supprimés: {len(df) - len(df_clean)}")
    
    # 2. Nettoyer les dates
    if 'date_publication' in df_clean.columns:
        # Remplacer les dates invalides
        df_clean['date_publication'] = df_clean['date_publication'].replace({
            'Date non trouvée': np.nan,
            '': np.nan
        })
    
    # 3. Nettoyer les textes
    colonnes_texte = ['titre', 'contenu', 'resume_50_mots', 'resume_100_mots', 'resume_150_mots']
    for col in colonnes_texte:
        if col in df_clean.columns:
            # Supprimer les espaces multiples
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
            # Supprimer les espaces en début/fin
            df_clean[col] = df_clean[col].str.strip()
            # Remplacer les chaînes vides par NaN
            df_clean[col] = df_clean[col].replace('', np.nan)
    
    # 4. Standardiser les langues
    if 'langue' in df_clean.columns:
        df_clean['langue'] = df_clean['langue'].str.capitalize()
    
    # 5. Nettoyer les nombres
    if 'nombre_mots' in df_clean.columns:
        df_clean['nombre_mots'] = pd.to_numeric(df_clean['nombre_mots'], errors='coerce').fillna(0).astype(int)
    if 'nombre_caracteres' in df_clean.columns:
        df_clean['nombre_caracteres'] = pd.to_numeric(df_clean['nombre_caracteres'], errors='coerce').fillna(0).astype(int)
    
    print("Nettoyage terminé!")
    return df_clean

# Charger et vérifier les données
if __name__ == "__main__":
    try:
        df = pd.read_csv('dataset_maladies_animales.csv')
        print(f"Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Vérifier avant nettoyage
        verifier_pretraitement(df)
        
        # Nettoyer les données
        df_clean = nettoyer_donnees(df)
        
        # Vérifier après nettoyage
        print("\n" + "="*50)
        print("APRÈS NETTOYAGE:")
        verifier_pretraitement(df_clean)
        
        # Sauvegarder la version nettoyée
        df_clean.to_csv('dataset_maladies_animales_clean.csv', index=False, encoding='utf-8')
        print(f"\nDataset nettoyé sauvegardé: dataset_maladies_animales_clean.csv")
        
    except FileNotFoundError:
        print("Le fichier dataset_maladies_animales.csv n'existe pas. Exécutez d'abord le script d'extraction.")