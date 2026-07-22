# 🐄 Animal Disease News Analysis

## 📌 Project Overview

This project aims to collect, clean, analyze, and visualize news related to animal diseases from multiple online sources.

The application automatically extracts information from news articles, preprocesses the collected data, and provides an interactive dashboard for exploratory data analysis.

This project was developed as part of a Data Science academic project.

---

## 🎯 Objectives

- Scrape animal disease news from multiple websites
- Extract useful metadata automatically
- Clean and preprocess the collected data
- Perform exploratory data analysis (EDA)
- Build an interactive dashboard using Streamlit

---

## 🛠️ Technologies Used

- Python 3.x
- Pandas
- NumPy
- BeautifulSoup
- Requests
- Streamlit
- Plotly
- Matplotlib
- Seaborn
- WordCloud

---

## 📂 Project Structure

```
Animal-Disease-News-Analysis/
│
├── projet.py                         # Web scraping & dataset generation
├── verification_pretraitement.py     # Data cleaning & preprocessing
├── dashboard_streamlit.py            # Interactive dashboard
│
├── dataset_maladies_animales.csv
├── dataset_maladies_animales_clean.csv
│
├── dashboard_maladies_animales.png
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Features

### Web Scraping

- Collects news articles from different websites
- Detects article language
- Extracts:
  - Title
  - Content
  - Publication date
  - Disease name
  - Geographic location
  - Organizations
  - Animals
- Generates summaries of:
  - 50 words
  - 100 words
  - 150 words

---

### Data Preprocessing

- Missing values handling
- Duplicate removal
- Text cleaning
- Date normalization
- Language standardization
- Data quality verification

---

### Dashboard

Interactive dashboard with:

- KPIs
- Disease distribution
- Language distribution
- Publication source analysis
- Geographic analysis
- Article length distribution
- Data filtering
- CSV export

---

## 📊 Dataset

Each article contains:

| Feature | Description |
|----------|-------------|
| Title | News title |
| Content | Full article |
| Language | Detected language |
| Disease | Identified disease |
| Publication Date | Article date |
| Location | Geographic location |
| Organizations | Named organizations |
| Animals | Mentioned animals |
| Number of Words | Article length |
| Summaries | 50 / 100 / 150 words |

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/your_username/Animal-Disease-News-Analysis.git
```

Go inside the project

```bash
cd Animal-Disease-News-Analysis
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Generate the dataset

```bash
python projet.py
```

### Clean the dataset

```bash
python verification_pretraitement.py
```

### Launch the dashboard

```bash
streamlit run dashboard_streamlit.py
```

---

## 📈 Dashboard Preview

The dashboard provides:

- Interactive filters
- Charts
- Statistics
- CSV export
- Disease analysis
- Source analysis
- Language analysis

---

## 📚 Future Improvements

- NLP with spaCy
- Sentiment Analysis
- Topic Modeling
- Machine Learning classification
- Named Entity Recognition (NER)
- Automatic disease prediction
- Docker deployment
- Cloud deployment
- CI/CD integration

---

 👨‍💻 Author

Melek Habessi

Master's Student in Data Science

Faculty of Economics and Management of Tunis

---

## 📜 License

This project is intended for educational and research purposes.
