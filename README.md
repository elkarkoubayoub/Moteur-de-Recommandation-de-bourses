
# 🎓 Scholarship Recommendation System

## 📌 Description

Ce projet est un système intelligent de recommandation de bourses d'études basé sur Python.

Il permet :

* 🔍 Rechercher des bourses adaptées à un profil étudiant
* 🧠 Générer des recommandations avec scoring
* 📄 Générer automatiquement un CV PDF
* ✉️ Générer une lettre de motivation
* 🤖 Intégration avec un chatbot (Botpress)

---

## 🏗️ Architecture du projet

```bash
MOTEUR RECOMMANDATION/
│── app.py                # API Flask principale
│── recommend.py         # Logique du moteur de recommandation
│── cv_generator.py      # Génération de CV PDF
│── lm_generator.py      # Génération lettre motivation
│── run_recommendation.py
│── test_profiles.py
│── requirements.txt
│
├── data
│   ├── scholarships.csv
│   └── scholarships_dataset.json
│
├── outputs/             # CV + lettres générés
├── .venv/
└── __pycache__/
```

---

## ⚙️ Technologies utilisées

* Python 🐍
* Flask (API REST)
* pandas (traitement données)
* JSON / CSV (dataset)
* Botpress (chatbot)
* CORS (connexion frontend)

---

## 🚀 Installation

```bash
git clone https://github.com/ton-username/scholarship-engine.git
cd scholarship-engine
```

```bash
pip install -r requirements.txt
```

---

## ▶️ Lancer le projet

```bash
python app.py
```

API disponible sur :

```
http://127.0.0.1:5000
```

---

## 🔗 Endpoints API

### 📌 1. Recommandation de bourses

```http
POST /recommend
```

#### Exemple JSON :

```json
{
  "name": "Ayoub",
  "level": "licence",
  "field": "informatique",
  "country": "France",
  "gpa": 14
}
```

#### Réponse :

```json
[
  {
    "name": "Eiffel Scholarship",
    "score": 90
  }
]
```

---

### 📄 2. Génération CV

* Génère un fichier PDF dans `/outputs`

---

### ✉️ 3. Lettre de motivation

* Génère un fichier `.txt` ou `.pdf`

---

## 🧠 Logique du moteur

Le moteur fonctionne avec :

### 🎯 Matching + Scoring

* Pays → + points
* Domaine → + points
* Niveau → + points
* GPA → + points

### 📊 Étapes :

1. Chargement dataset (CSV/JSON)
2. Filtrage des bourses
3. Calcul score
4. Tri des résultats
5. Retour Top N

---

## 🤖 Intégration Chatbot

Le projet est connecté à **Botpress** :

1. Utilisateur parle avec le bot
2. Botpress envoie le profil à `/recommend`
3. API retourne les résultats
4. Bot affiche les bourses

---

## 📁 Outputs générés

Tous les fichiers sont stockés dans :

```bash
/outputs/
```

Exemples :

* `CV_Ayoub.pdf`
* `Motivation_Letter.txt`

---

## 🧪 Tests

```bash
python test_profiles.py
```

---

## 📈 Améliorations futures

* Machine Learning (KNN, AI)
* Interface web (dashboard)
* Notifications automatiques
* Connexion Airtable / DB cloud
* Déploiement (Render, Railway)

---

## 👨‍💻 Auteur

**Ayoub El Karkoub & Majda Rane**

