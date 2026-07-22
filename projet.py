# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import random
from urllib.parse import urlparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import warnings
warnings.filterwarnings('ignore')

class AnimalDiseaseNewsExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def detect_language(self, text):
        """Détecter la langue du texte"""
        if not text:
            return "Inconnu"
        
        # Détection basique basée sur les caractères
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        french_indicators = len(re.findall(r'\b(le|la|les|de|des|du|et|est|à|dans|pour|sur|qui|que)\b', text.lower()))
        english_indicators = len(re.findall(r'\b(the|and|for|are|with|this|that|from|have|was)\b', text.lower()))
        
        if arabic_chars > 100:
            return "Arabe"
        elif french_indicators > english_indicators:
            return "Français"
        elif english_indicators > french_indicators:
            return "Anglais"
        else:
            return "Inconnu"
    
    def extract_date(self, soup, url):
        """Extraire la date de publication"""
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2}\s+\w+\s+\d{4}',
        ]
        
        # Recherche dans les balises meta
        meta_date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="date"]',
            'meta[property="og:published_time"]',
            'time[datetime]'
        ]
        
        for selector in meta_date_selectors:
            element = soup.select_one(selector)
            if element:
                date_content = element.get('content') or element.get('datetime') or element.get_text()
                for pattern in date_patterns:
                    match = re.search(pattern, date_content)
                    if match:
                        try:
                            date_str = match.group()
                            # Normaliser la date
                            date_str = re.sub(r'[/]', '-', date_str)
                            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                            return date_obj.strftime('%d-%m-%Y')
                        except:
                            continue
        
        # Recherche dans le texte
        text = soup.get_text()
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    date_str = re.sub(r'[/]', '-', match)
                    if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                    return date_obj.strftime('%d-%m-%Y')
                except:
                    continue
        
        return "Date non trouvée"
    
    def extract_location(self, text, soup):
        """Extraire le lieu concerné"""
        # Liste de pays et régions pour la détection
        locations = {
            'France': ['france', 'français', 'française', 'paris'],
            'USA': ['usa', 'united states', 'états-unis', 'us'],
            'UK': ['uk', 'united kingdom', 'royaume-uni', 'angleterre'],
            'Ireland': ['ireland', 'irlande'],
            'Italy': ['italy', 'italie'],
            'Brazil': ['brazil', 'brésil'],
            'India': ['india', 'inde'],
            'Senegal': ['senegal', 'sénégal'],
            'Central Africa': ['centrafrique', 'central africa'],
            'Morocco': ['morocco', 'maroc'],
            'Saudi Arabia': ['saudi arabia', 'arabie saoudite'],
            'Israel': ['israel', 'israël'],
            'Europe': ['europe', 'européen'],
            'Africa': ['africa', 'afrique'],
            'Asia': ['asia', 'asie']
        }
        
        text_lower = text.lower()
        found_locations = []
        
        for location, keywords in locations.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_locations.append(location)
                    break
        
        return ', '.join(set(found_locations)) if found_locations else "Lieu non spécifié"
    
    def extract_disease(self, text, default_disease):
        """Extraire le nom de la maladie"""
        diseases = {
            'Influenza aviaire': ['influenza aviaire', 'grippe aviaire', 'avian flu', 'أنفلونزا الطيور'],
            'Peste porcine africaine': ['peste porcine africaine', 'african swine fever', 'peste porcine'],
            'Fièvre aphteuse': ['fièvre aphteuse', 'foot and mouth disease'],
            'Dermatose Nodulaire Contagieuse': ['dermatose nodulaire contagieuse', 'lumpy skin disease'],
            'Fièvre de la Vallée du Rift': ['fièvre de la vallée du rift', 'rift valley fever', 'حمى الوادي المتصدع'],
            'Bluetongue': ['bluetongue', 'fièvre catarrhale ovine'],
            'Rage': ['rage', 'rabies'],
            'Maladie Hémorragique Épizootique': ['maladie hémorragique épizootique', 'mhe'],
            'Peste bovine': ['peste bovine', 'rinderpest'],
            'Peste équine africaine': ['peste équine africaine', 'african horse sickness'],
            'Peste des petits ruminants': ['peste des petits ruminants'],
            'Brucellose': ['brucellose', 'brucellosis'],
            'MERS-CoV': ['mers-cov'],
            'Variole du dromadaire': ['variole du dromadaire', 'camel pox'],
            'Rhinotrachéite bovine infectieuse': ['rhinotrachéite bovine infectieuse'],
            'Mpox': ['mpox', 'monkeypox']
        }
        
        text_lower = text.lower()
        for disease, keywords in diseases.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return disease
        
        return default_disease
    
    def extract_entities(self, text):
        """Extraire les entités nommées"""
        entities = {
            'organizations': [],
            'animals': []
        }
        
        # Organisations
        org_patterns = [
            r'OMS|WHO',
            r'WOAH|OIE',
            r'FAO',
            r'CDC',
            r'FDA',
            r'Ministère',
            r'GDS',
            r'Anses',
            r'Sénat',
            r'Préfecture'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['organizations'].extend(matches)
        
        # Animaux
        animal_patterns = [
            r'volailles?',
            r'porcs?',
            r'bovins?',
            r'ovins?',
            r'caprins?',
            r'chameaux?',
            r'dromadaires?',
            r'chevaux?',
            r'chauves-souris',
            r'animaux?'
        ]
        
        for pattern in animal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['animals'].extend(matches)
        
        # Nettoyer et dédupliquer
        entities['organizations'] = list(set(entities['organizations']))
        entities['animals'] = list(set(entities['animals']))
        
        return entities
    
    def generate_summary(self, text, word_count):
        """Générer un résumé de longueur spécifique"""
        if not text:
            return ""
        
        words = text.split()
        if len(words) <= word_count:
            return text
        
        # Prendre les premiers mots
        summary_words = words[:word_count]
        return ' '.join(summary_words)
    
    def extract_news_content(self, url, default_lang, default_disease):
        """Extraire le contenu d'une URL"""
        try:
            print(f"Extraction de: {url}")
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire le titre
            title = ""
            title_selectors = [
                'h1',
                'title',
                'meta[property="og:title"]',
                '.article-title',
                '.title',
                '#title'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title_content = element.get('content') or element.get_text(strip=True)
                    if title_content and len(title_content) > 10:
                        title = title_content
                        break
            
            # Extraire le contenu principal
            content = ""
            content_selectors = [
                'article',
                '.article-content',
                '.content',
                '.post-content',
                'main',
                '.main-content'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 200:  # Contenu significatif
                        content = text
                        break
                if content:
                    break
            
            # Si pas de contenu structuré, prendre tout le texte
            if not content:
                content = soup.get_text(strip=True)
            
            # Nettoyer le contenu
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Détecter la langue
            lang = self.detect_language(content) if content else default_lang
            
            # Statistiques
            char_count = len(content) if content else 0
            word_count = len(content.split()) if content else 0
            
            # Extraire la date
            date = self.extract_date(soup, url)
            
            # Extraire le lieu
            location = self.extract_location(content, soup)
            
            # Identifier la maladie
            disease = self.extract_disease(content, default_disease)
            
            # Déterminer la source
            source_domain = urlparse(url).netloc.lower()
            if any(org in source_domain for org in ['gouv.fr', 'gov.', 'senat.fr', 'who.int', 'woah.org', 'fao.org', 'anses.fr']):
                source_type = "Site officiel"
            elif any(media in source_domain for media in ['lemonde.fr', 'lefigaro.fr', 'reuters.com', 'apnews.com', 'aljazeera.net', 'bbc.com', 'theguardian.com']):
                source_type = "Médias"
            else:
                source_type = "Autre"
            
            # Générer les résumés
            summary_50 = self.generate_summary(content, 50)
            summary_100 = self.generate_summary(content, 100)
            summary_150 = self.generate_summary(content, 150)
            
            # Extraire les entités nommées
            entities = self.extract_entities(content)
            
            return {
                'url': url,
                'titre': title,
                'contenu': content,
                'langue': lang,
                'nombre_caracteres': char_count,
                'nombre_mots': word_count,
                'date_publication': date,
                'lieu': location,
                'maladie': disease,
                'source_publication': source_type,
                'resume_50_mots': summary_50,
                'resume_100_mots': summary_100,
                'resume_150_mots': summary_150,
                'organisations': ', '.join(entities['organizations']),
                'animaux': ', '.join(entities['animals']),
                'statut': 'Succès'
            }
            
        except Exception as e:
            print(f"Erreur lors de l'extraction de {url}: {str(e)}")
            return {
                'url': url,
                'titre': '',
                'contenu': '',
                'langue': default_lang,
                'nombre_caracteres': 0,
                'nombre_mots': 0,
                'date_publication': 'Date non trouvée',
                'lieu': 'Lieu non spécifié',
                'maladie': default_disease,
                'source_publication': 'Inconnu',
                'resume_50_mots': '',
                'resume_100_mots': '',
                'resume_150_mots': '',
                'organisations': '',
                'animaux': '',
                'statut': f'Erreur: {str(e)}'
            }

def main():
    # Initialiser l'extracteur
    extractor = AnimalDiseaseNewsExtractor()
    
    # Charger les URLs depuis le fichier Excel
    try:
        df_urls = pd.read_excel('urls.xlsx')
        print("Fichier URLs chargé avec succès")
    except:
        # Créer un DataFrame avec les URLs fournies
        data = {
            'No.': range(1, 51),
            'URL': [
                "https://agriculture.gouv.fr/communique-de-presse/influenza-aviaire-hautement-pathogene-la-france-place-son-territoire-en-niveau-de-risque-eleve",
                "https://www.senat.fr/leg/ppl24-910.html",
                "https://www.seine-maritime.gouv.fr/Actualites/Influenza-aviaire-la-France-place-son-territoire-en-niveau-de-risque-eleve",
                "https://www.gdsfrance.org/actualites/dermatose-nodulaire-contagieuse",
                "https://www.gdsfrance.org/actualites/fievre-aphteuse-une-reelle-menace",
                "https://www.woah.org/app/uploads/2025/01/asf-report-60.pdf",
                "https://apnews.com/article/taiwan-african-swine-fever-first-cases-884ad332e27185c1c7cbec6203193ace",
                "https://africainside.net/14-01-25938-Centrafrique-Alerte-a-la-fievre-de-la-vallee-du-Rift2745181385.html",
                "https://afrique.le360.ma/societe/senegal-la-fievre-de-la-vallee-du-rift-fait-quatre-morts_H6LC6Q73YNB6DO7M2GKZBZ4JC4/",
                "https://www.seneweb.com/fr/news/Sante/le-ministere-de-la-sante-alerte-277-cas-confirmes-22-deces-lies-a-la-fievre-de-la-vallee-du-rift-et-de-mpox_n_471892.html",
                "https://www.who.int/ar/emergencies/disease-outbreak-news/item/2024-DON511",
                "https://www.who.int/ar/emergencies/disease-outbreak-news/item/2024-DON512",
                "https://www.gov.il/ar/pages/avian_flu_mishmar_hamek",
                "https://www.aljazeera.net/health/2024/12/18/%D8%A7%D9%84%D9%85%D8%B5%D8%A7%D8%A8-%D8%AA%D8%B9%D8%B1%D8%B6-%D9%84%D8%B7%D9%8A%D9%88%D8%B1-%D9%85%D8%B1%D9%8A%D8%B6%D8%A9-%D9%88%D9%85%D9%8A%D8%AA%D8%A9-%D9%8A%D8%B1%D8%A8%D9%8A%D9%87%D8%A7",
                "https://www.gov.uk/government/news/bluetongue-confirmed-in-a-sheep-in-norfolk-england",
                "https://www.animalhealthsurveillance.agriculture.gov.ie/media/Bluetongue%20Update%20No.%207%20of%202024.pdf",
                "https://www.gov.uk/government/publications/bluetongue-virus-in-europe/15-march-2024-updated-outbreak-assessment-for-bluetongue-virus-in-europe",
                "https://www.woah.org/en/article/woah-launches-report-on-the-global-status-of-rabies-control/",
                "https://www.woah.org/en/article/woah-releases-new-strategy-for-rabies-control-in-asia-and-the-pacific/",
                "https://www.cdc.gov/flu/avianflu/spotlights/2024-2025/avian-flu-in-dairy-cattle.htm",
                "https://www.fda.gov/animal-veterinary/cvm-updates/fda-announces-data-demonstrating-inactivation-h5n1-virus-pasteurized-milk",
                "https://www.reuters.com/business/healthcare-pharmaceuticals/us-tests-show-h5n1-bird-flu-not-in-meat-supply-fda-agriculture-officials-say-2024-05-02/",
                "https://www.lemonde.fr/planete/article/2024/04/10/epidemie-de-grippe-aviaire-chez-des-vaches-laitieres-aux-etats-unis_6227091_3244.html",
                "https://www.franceagrimer.fr/content/download/74889/document/Note%20de%20conjoncture%20Ovins-Caprins%20-%20avril%202024.pdf",
                "https://www.anses.fr/fr/content/epidemie-de-mhe-dans-le-sud-ouest-lanses-alerte-sur-le-risque-de-propagation",
                "https://www.woah.org/en/event/2024-woah-regional-workshop-on-lumpy-skin-disease-control-for-south-asia/",
                "https://www.theguardian.com/environment/2024/jan/09/russia-says-it-has-created-first-world-vaccine-against-african-swine-fever",
                "https://www.oie.int/en/rinderpest-a-century-of-woah-and-eradication/",
                "https://www.woah.org/en/document/african-horse-sickness-situation-report-2024/",
                "https://www.who.int/ar/news-room/fact-sheets/detail/rift-valley-fever",
                "https://www.fao.org/newsroom/detail/FAO-steps-up-efforts-to-tackle-peste-des-petits-ruminants/en",
                "https://www.gds-bretagne.fr/actualites/mhe-point-sur-la-situation-et-les-mesures-de-lutte",
                "https://www.who.int/news-room/detail/07-11-2024-mers-cov-in-camels-and-humans-in-saudi-arabia",
                "https://www.reuters.com/world/middle-east/gulf-veterinary-authorities-on-alert-after-camel-pox-outbreak-2024-03-20/",
                "https://www.ansa.it/english/news/general_news/2024/09/10/lumpy-skin-disease-emergency-in-southern-italy_28f73117-6490-449e-8c33-e020275d31c4.html",
                "https://www.lefigaro.fr/flash-actu/l-influenza-aviaire-frappe-un-premier-elevage-de-volailles-en-bresil-20240905",
                "https://www.woah.org/en/document/brucellosis-in-animals-situation-report-2024/",
                "https://www.anses.fr/fr/content/la-brucellose-une-maladie-animale-surveiller",
                "https://www.fao.org/africa/news/detail/en/c/1691456/",
                "https://www.dw.com/ar/%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%84%D8%A7%D8%AA-%D8%A7%D9%84%D8%AC%D8%AF%D9%8A%D8%AF%D8%A9-%D9%85%D9%86-%D8%A3%D9%86%D9%81%D9%84%D9%88%D9%86%D8%B2%D8%A7-%D8%A7%D9%84%D8%B7%D9%8A%D9%88%D8%B1-%D8%A7%D9%84%D9%85%D8%B3%D8%AA%D9%81%D8%AD%D9%84-%D9%81%D9%8A-%D8%A7%D9%84%D8%B9%D8%A7%D9%84%D9%85/a-68521509",
                "https://www.reuters.com/business/healthcare-pharmaceuticals/who-concerned-about-h5n1-avian-flu-cases-mammals-urges-vigilance-2024-04-12/",
                "https://www.woah.org/en/disease/infectious-bovine-rhinotracheitis/",
                "https://www.leparisien.fr/societe/sante/la-peste-porcine-africaine-se-rapproche-de-la-france-les-autorites-renforcent-la-surveillance-2024-06-18-508I3W274E824A485A.php",
                "https://www.bfmtv.com/economie/agriculture/peste-porcine-africaine-un-risque-eleve-de-propagation-en-europe-selon-l-agence-europeenne-de-securite-alimentaire_AD-202403130198.html",
                "https://www.bbc.com/news/world-asia-india-68936611",
                "https://www.woah.org/en/document/foot-and-mouth-disease-situation-report-2024/",
                "https://www.fao.org/animal-health/news-events/news/detail/en/c/1699933/",
                "https://www.lemonde.fr/afrique/article/2024/02/29/en-afrique-l-epidemie-de-dermatose-nodulaire-contagieuse-se-propage_6219356_3212.html",
                "https://www.who.int/ar/emergencies/disease-outbreak-news/item/2024-DON519",
                "https://www.gdsfrance.org/actualites/mhe-la-vaccination-des-troupeaux-une-solution-qui-se-prepare"
            ],
            'Langue': ['Français'] * 10 + ['Arabe'] * 4 + ['Anglais'] * 36,
            'Sujet Principal': [
                'Influenza aviaire', 'Propositions de loi sur la santé animale', 'Influenza aviaire',
                'Dermatose Nodulaire Contagieuse', 'Fièvre Aphteuse', 'Peste porcine africaine (Rapport)',
                'Peste porcine africaine', 'Fièvre de la Vallée du Rift', 'Fièvre de la Vallée du Rift',
                'Fièvre de la Vallée du Rift / Mpox', 'أنفلونزا الطيور (H5N1)', 'أنفلونزا الطيور (H5N1)',
                'أنفلونزا الطيور', 'أنفلونزا الطيور (H5N1)', 'Bluetongue (BTV-3)', 'Bluetongue (Rapport)',
                'Bluetongue (BTV-1, BTV-4)', 'Rage', 'Rage', 'Grippe aviaire chez les bovins',
                'Grippe aviaire (Lait)', 'Grippe aviaire (Viande)', 'Grippe aviaire chez les bovins',
                'Fièvre Catarrhale Ovine (Rapport)', 'Maladie Hémorragique Épizootique (MHE)',
                'Dermatose Nodulaire Contagieuse', 'Peste porcine africaine (Vaccin)', 'Peste bovine (Éradication)',
                'Peste équine africaine (Rapport)', 'حمى الوادي المتصدع (Fiche)', 'Peste des petits ruminants',
                'Maladie Hémorragique Épizootique (MHE)', 'MERS-CoV (Chameaux)', 'Variole du dromadaire',
                'Dermatose Nodulaire Contagieuse', 'Influenza aviaire (Brésil)', 'Brucellose (Rapport)',
                'Brucellose', 'Peste des petits ruminants (Afrique)', 'أنفلونزا الطيور (Analyses)',
                'Grippe aviaire (Mammifères)', 'Rhinotrachéite bovine infectieuse', 'Peste porcine africaine',
                'Peste porcine africaine (Europe)', 'Peste porcine africaine (Inde)', 'Fièvre aphteuse (Rapport)',
                'Fièvre aphteuse (Arménie)', 'Dermatose Nodulaire Contagieuse (Afrique)', 'حمى ماربورغ (Animaux/Chauves-souris)',
                'MHE (Vaccination)'
            ],
            'Source (Indicative)': [
                'Ministère de l\'Agriculture', 'Sénat (Officiel)', 'Préfecture', 'GDS France', 'GDS France',
                'WOAH (Officiel)', 'Associated Press (Média)', 'Africa Inside (Média)', 'Le360 Afrique (Média)',
                'Seneweb (Média)', 'OMS (Officiel)', 'OMS (Officiel)', 'Ministère Agriculture Israël (Officiel)',
                'Al Jazeera (Média)', 'GOV.UK (Officiel)', 'AHS Ireland (Officiel)', 'GOV.UK (Officiel)',
                'WOAH (Officiel)', 'WOAH (Officiel)', 'CDC (Officiel)', 'FDA (Officiel)', 'Reuters (Média)',
                'Le Monde (Média)', 'FranceAgriMer (Officiel)', 'Anses (Officiel)', 'WOAH (Officiel)',
                'The Guardian (Média)', 'OIE / WOAH (Officiel)', 'WOAH (Officiel)', 'OMS (Officiel)',
                'FAO (Officiel)', 'GDS Bretagne', 'OMS (Officiel)', 'Reuters (Média)', 'ANSA (Média)',
                'Le Figaro (Média)', 'WOAH (Officiel)', 'Anses (Officiel)', 'FAO (Officiel)', 'DW (Média)',
                'Reuters (Média)', 'WOAH (Fiche d\'info)', 'Le Parisien (Média)', 'BFM TV (Média)', 'BBC (Média)',
                'WOAH (Officiel)', 'FAO (Officiel)', 'Le Monde (Média)', 'OMS (Officiel)', 'GDS France'
            ]
        }
        df_urls = pd.DataFrame(data)
    
    # Extraire les données de chaque URL
    news_data = []
    
    for index, row in df_urls.iterrows():
        url = row['URL']
        default_lang = row['Langue']
        default_disease = row['Sujet Principal']
        
        # Extraire les données
        news_item = extractor.extract_news_content(url, default_lang, default_disease)
        news_data.append(news_item)
        
        # Pause pour éviter de surcharger les serveurs
        time.sleep(random.uniform(1, 3))
        
        # Afficher la progression
        print(f"Progression: {index + 1}/{len(df_urls)} - {news_item['statut']}")
    
    # Créer le DataFrame final
    df_final = pd.DataFrame(news_data)
    
    # Sauvegarder en CSV
    df_final.to_csv('dataset_maladies_animales.csv', index=False, encoding='utf-8')
    print("Dataset sauvegardé dans 'dataset_maladies_animales.csv'")
    
    # Afficher les statistiques
    print(f"\nStatistiques d'extraction:")
    print(f"Total URLs: {len(df_final)}")
    print(f"Succès: {len(df_final[df_final['statut'] == 'Succès'])}")
    print(f"Erreurs: {len(df_final[df_final['statut'] != 'Succès'])}")
    
    # Créer le dashboard
    create_dashboard(df_final)
    
    return df_final

def create_dashboard(df):
    """Créer un dashboard de visualisation"""
    print("\nCréation du dashboard...")
    
    # Filtrer seulement les extractions réussies
    df_success = df[df['statut'] == 'Succès']
    
    if len(df_success) == 0:
        print("Aucune donnée valide pour créer le dashboard")
        return
    
    # Configuration des graphiques
    plt.style.use('default')
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Dashboard - Analyse des Actualités sur les Maladies Animales', fontsize=16, fontweight='bold')
    
    # 1. Distribution par langue
    lang_counts = df_success['langue'].value_counts()
    axes[0, 0].pie(lang_counts.values, labels=lang_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 0].set_title('Distribution par Langue')
    
    # 2. Distribution par maladie
    disease_counts = df_success['maladie'].value_counts().head(10)
    axes[0, 1].barh(range(len(disease_counts)), disease_counts.values)
    axes[0, 1].set_yticks(range(len(disease_counts)))
    axes[0, 1].set_yticklabels(disease_counts.index)
    axes[0, 1].set_title('Top 10 des Maladies')
    axes[0, 1].set_xlabel('Nombre d\'articles')
    
    # 3. Distribution par source
    source_counts = df_success['source_publication'].value_counts()
    axes[0, 2].bar(source_counts.index, source_counts.values)
    axes[0, 2].set_title('Distribution par Source')
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # 4. Distribution par lieu
    location_counts = df_success['lieu'].value_counts().head(8)
    axes[1, 0].bar(location_counts.index, location_counts.values)
    axes[1, 0].set_title('Top 8 des Lieux')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 5. Distribution de la longueur des articles
    axes[1, 1].hist(df_success['nombre_mots'], bins=20, alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Distribution du Nombre de Mots')
    axes[1, 1].set_xlabel('Nombre de mots')
    axes[1, 1].set_ylabel('Fréquence')
    
    # 6. Statut d'extraction
    status_counts = df['statut'].value_counts()
    axes[1, 2].bar([str(s)[:20] for s in status_counts.index], status_counts.values)
    axes[1, 2].set_title('Statut d\'Extraction')
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('dashboard_maladies_animales.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Afficher les statistiques numériques
    print("\n=== STATISTIQUES DU DATASET ===")
    print(f"Nombre total d'articles: {len(df)}")
    print(f"Articles extraits avec succès: {len(df_success)}")
    print(f"Taux de réussite: {len(df_success)/len(df)*100:.1f}%")
    
    if len(df_success) > 0:
        print(f"\n=== STATISTIQUES DE LONGUEUR ===")
        print(f"Nombre moyen de mots: {df_success['nombre_mots'].mean():.0f}")
        print(f"Nombre minimum de mots: {df_success['nombre_mots'].min()}")
        print(f"Nombre maximum de mots: {df_success['nombre_mots'].max()}")
        print(f"Nombre moyen de caractères: {df_success['nombre_caracteres'].mean():.0f}")
        
        print(f"\n=== DISTRIBUTION PAR LANGUE ===")
        for lang, count in lang_counts.items():
            print(f"{lang}: {count} articles ({count/len(df_success)*100:.1f}%)")
        
        print(f"\n=== DISTRIBUTION PAR SOURCE ===")
        for source, count in source_counts.items():
            print(f"{source}: {count} articles")

if __name__ == "__main__":
    # Exécuter le projet
    df_result = main()
    
    # Afficher un aperçu du dataset
    print("\n=== APERÇU DU DATASET ===")
    print(df_result.head())
    
    print("\nProjet terminé avec succès!")
    print("Fichiers générés:")
    print("- dataset_maladies_animales.csv (le dataset complet)")
    print("- dashboard_maladies_animales.png (le dashboard)")