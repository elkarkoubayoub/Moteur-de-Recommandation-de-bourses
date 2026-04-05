"""
recommend.py – Moteur de recommandation de bourses (SCHOLARLY)
──────────────────────────────────────────────────────────────────
Fonctions publiques :
  • load_scholarships(path)  → list[dict]   (JSON ou CSV)
  • filter_hard(scholarships, profile)      → list[dict]
  • compute_score(scholarship, profile)     → int (0-100)
  • recommend(profile, top_n, dataset_path) → dict   (compatible app.py)
"""

import json
import os
import math
import pandas as pd

# ════════════════════════════════════════════════════════════════════════════
# Pondération par pays  (coefficient × 100 → points sur 100)
# USA = 0.30  →  30 pts
# ════════════════════════════════════════════════════════════════════════════
COUNTRY_WEIGHTS = {
    "usa":            0.30,
    "france":         0.28,
    "uk":             0.27,
    "germany":        0.26,
    "canada":         0.25,
    "australia":      0.24,
    "switzerland":    0.24,
    "netherlands":    0.23,
    "sweden":         0.23,
    "italy":          0.22,
    "turkey":         0.22,
    "japan":          0.22,
    "south korea":    0.22,
    "china":          0.21,
    "morocco":        0.21,
    "uae":            0.21,
    "slovenia":       0.20,
    "kazakhstan":     0.20,
    "hungary":        0.20,
    "european union": 0.20,
    "international":  0.19,
}

# Barème maximum (somme = 100 pts)
# Niveau       : 25 pts
# Domaine      : 25 pts
# Pays cible   : weight × 100  (ex: USA → 30 pts)
# GPA          : 15 pts
# Popularité   :  5 pts bonus  (si popularity_score > 85)


# ════════════════════════════════════════════════════════════════════════════
# 1. Chargement de la base (JSON ou CSV)
# ════════════════════════════════════════════════════════════════════════════
def _load_json(path: str) -> list:
    """Charge le fichier JSON de bourses et retourne une liste de dicts."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: str) -> list:
    """
    Charge le fichier CSV (colonnes françaises) et le convertit en liste
    de dicts au même format que le JSON.
    """
    col_map = {
        "ID":                              "id",
        "Titre":                           "title",
        "Université":                      "university",
        "Pays":                            "country",
        "Niveau(x)":                       "level",
        "Domaines d'étude":                "field_of_study",
        "Catégorie":                       "category",
        "Type de financement":             "funding_type",
        "Montant":                         "award",
        "Devise":                          "currency",
        "Date limite":                     "deadline",
        "Statut":                          "status",
        "Nationalité éligible":            "eligibility.nationality",
        "GPA minimum":                     "eligibility.GPA_min",
        "Test de langue":                  "eligibility.language_requirement.test",
        "Score minimum":                   "eligibility.language_requirement.min_score",
        "Limite d'âge":                    "eligibility.age_limit",
        "Expérience requise":              "eligibility.experience_required",
        "Lien de candidature":             "application_link",
        "Score popularité":                "popularity_score",
        "Score difficulté":                "difficulty_score",
    }
    df = pd.read_csv(path)
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    df["eligibility.GPA_min"] = pd.to_numeric(df.get("eligibility.GPA_min", 0), errors="coerce")

    records = []
    for _, row in df.iterrows():
        # Reconstituer la structure imbriquée proche du JSON
        level_raw = str(row.get("level", ""))
        field_raw = str(row.get("field_of_study", ""))
        record = {
            "id":           str(row.get("id", "")),
            "title":        str(row.get("title", "")),
            "university":   str(row.get("university", "")),
            "country":      str(row.get("country", "")),
            "level":        [l.strip() for l in level_raw.split(",") if l.strip()],
            "field_of_study": [f.strip() for f in field_raw.split(",") if f.strip()],
            "category":     str(row.get("category", "")),
            "funding_type": str(row.get("funding_type", "")),
            "award":        row.get("award"),
            "currency":     str(row.get("currency", "")),
            "deadline":     str(row.get("deadline", "")),
            "status":       str(row.get("status", "")).lower(),
            "eligibility": {
                "nationality": str(row.get("eligibility.nationality", "")),
                "GPA_min":     float(row["eligibility.GPA_min"])
                               if not pd.isna(row.get("eligibility.GPA_min")) else 0.0,
                "language_requirement": {
                    "test":      str(row.get("eligibility.language_requirement.test", "")),
                    "min_score": row.get("eligibility.language_requirement.min_score"),
                },
                "age_limit":          row.get("eligibility.age_limit"),
                "experience_required": row.get("eligibility.experience_required"),
            },
            "application_link": str(row.get("application_link", "")),
            "popularity_score": float(row["popularity_score"])
                                if not pd.isna(row.get("popularity_score")) else 0.0,
            "difficulty_score": float(row["difficulty_score"])
                                if not pd.isna(row.get("difficulty_score")) else 0.0,
        }
        records.append(record)
    return records


def load_scholarships(path: str) -> list:
    """
    Charge la base de bourses depuis un fichier JSON ou CSV.
    Choisit automatiquement le format selon l'extension.
    Si le CSV est introuvable mais qu'un JSON du même nom de base existe, l'utilise.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".json":
        return _load_json(path)

    # CSV demandé → essaie d'abord le CSV, puis le JSON du même répertoire
    if ext == ".csv":
        if os.path.exists(path):
            return _load_csv(path)
        # Fallback automatique vers scholarships_dataset.json
        base_dir = os.path.dirname(path) or "."
        json_path = os.path.join(base_dir, "scholarships_dataset.json")
        if os.path.exists(json_path):
            return _load_json(json_path)

    raise FileNotFoundError(f"Base de données introuvable : {path}")


# ════════════════════════════════════════════════════════════════════════════
# 2. Filtre dur  (critères éliminatoires)
# ════════════════════════════════════════════════════════════════════════════
def _nationality_ok(sch: dict, student_nationality: str) -> bool:
    """
    Vérifie si la nationalité de l'étudiant est acceptée par la bourse.
    Accepte 'All nationalities', 'International', NaN, etc.
    """
    nat_req = str(sch.get("eligibility", {}).get("nationality", "")).strip().lower()
    if not nat_req or nat_req in ("nan", "any", "all", "all nationalities", "international"):
        return True
    return student_nationality.lower() in nat_req


def filter_hard(scholarships: list, profile: dict) -> list:
    """
    Applique les filtres éliminatoires sur la liste de bourses.

    Critères obligatoires :
      ① Pays cible  – la bourse doit être dans le pays demandé
      ② Niveau      – le niveau de l'étudiant doit figurer dans les niveaux de la bourse
      ③ GPA         – le GPA de l'étudiant ≥ GPA minimum requis
      ④ Statut      – la bourse doit être « open »

    Retourne la liste filtrée.
    """
    target_country  = profile.get("target_country", "").strip().lower()
    student_level   = profile.get("level", "").strip().lower()
    student_gpa     = float(profile.get("gpa", 0))
    student_nat     = profile.get("nationality", "").strip().lower()

    kept = []
    for sch in scholarships:
        # ① Pays cible
        country = sch.get("country", "").strip().lower()
        if target_country and target_country not in country:
            continue

        # ② Niveau (liste)
        levels = [l.strip().lower() for l in sch.get("level", [])]
        if student_level and student_level not in levels:
            continue

        # ③ GPA minimum
        gpa_min = sch.get("eligibility", {}).get("GPA_min") or 0
        try:
            if student_gpa < float(gpa_min):
                continue
        except (TypeError, ValueError):
            pass

        # ④ Statut ouvert
        if sch.get("status", "").lower() == "closed":
            continue

        kept.append(sch)

    return kept


# ════════════════════════════════════════════════════════════════════════════
# 3. Calcul du score de compatibilité
# ════════════════════════════════════════════════════════════════════════════
def compute_score(sch: dict, profile: dict) -> int:
    """
    Calcule un score de compatibilité (0-100) entre une bourse et un profil.

    Barème :
      • Niveau       = 25 pts
      • Domaine      = 25 pts
      • Pays cible   = weight_pays × 100  (USA → 0.30 × 100 = 30 pts)
      • GPA ≥ min    = 15 pts
      • Popularité   =  5 pts bonus  (popularity_score > 85)
    """
    score = 0

    # ─── Niveau : 25 pts ─────────────────────────────────────────────────
    student_level = profile.get("level", "").strip().lower()
    levels = [l.strip().lower() for l in sch.get("level", [])]
    if student_level and student_level in levels:
        score += 25

    # ─── Domaine d'étude : 25 pts ────────────────────────────────────────
    student_field = profile.get("field", "").strip().lower()
    fields = [f.strip().lower() for f in sch.get("field_of_study", [])]
    # Match exact OU "all fields" dans la bourse
    field_match = any(
        f in ("all fields",) or (student_field and student_field in f)
        for f in fields
    )
    if student_field and field_match:
        score += 25

    # ─── Pays cible : pondération pays × 100 ────────────────────────────
    target = profile.get("target_country", "").strip().lower()
    country_sch = sch.get("country", "").strip().lower()
    if target and target in country_sch:
        pts = int(COUNTRY_WEIGHTS.get(target, 0.20) * 100)
        score += pts

    # ─── GPA : 15 pts ────────────────────────────────────────────────────
    student_gpa = profile.get("gpa")
    if student_gpa is not None:
        gpa_min = sch.get("eligibility", {}).get("GPA_min") or 0
        try:
            if float(student_gpa) >= float(gpa_min):
                score += 15
        except (TypeError, ValueError):
            pass

    # ─── Popularité : +5 pts bonus ───────────────────────────────────────
    pop = sch.get("popularity_score") or 0
    try:
        if float(pop) > 85:
            score += 5
    except (TypeError, ValueError):
        pass

    return min(score, 100)


# ════════════════════════════════════════════════════════════════════════════
# 4. Fonction principale  recommend()  — API compatible app.py
# ════════════════════════════════════════════════════════════════════════════
def recommend(profile: dict, top_n: int = 5,
              dataset_path: str = "scholarships.csv") -> dict:
    """
    Recommande les top_n bourses les plus compatibles avec le profil donné.

    Paramètres
    ----------
    profile : dict
        Clés attendues :
          - level          (str)  : "Master", "PhD", "Licence"
          - field          (str)  : domaine d'étude (ex: "Computer Science")
          - nationality    (str)  : nationalité (ex: "Morocco")
          - gpa            (float): GPA de l'étudiant (ex: 3.5)
          - target_country (str)  : pays cible (ex: "USA")
          - country        (str)  : alias accepté pour target_country (legacy)

    top_n : int
        Nombre de recommandations à retourner (défaut : 5).

    dataset_path : str
        Chemin vers le fichier de bourses (.json ou .csv).

    Retour
    ------
    dict : {"scholarships": [...]}   ou   ({"error": "..."}, code_http)
    """

    # Support de l'alias "country" → "target_country" (compatibilité legacy)
    if "target_country" not in profile and "country" in profile:
        profile = dict(profile)
        profile["target_country"] = profile["country"]

    # ── Chargement ──────────────────────────────────────────────────────────
    try:
        all_scholarships = load_scholarships(dataset_path)
    except FileNotFoundError:
        return {"error": "Base de données introuvable."}, 404

    # ── Filtre dur ──────────────────────────────────────────────────────────
    filtered = filter_hard(all_scholarships, profile)

    if not filtered:
        return {
            "scholarships": [],
            "message": "Aucune bourse ne correspond à ces critères.",
        }

    # ── Scoring & tri ────────────────────────────────────────────────────────
    scored = [
        (sch, compute_score(sch, profile))
        for sch in filtered
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:top_n]

    # ── Construction du résultat ─────────────────────────────────────────────
    result = []
    for sch, score in top:
        result.append({
            "id":               sch.get("id", ""),
            "name":             sch.get("title", "Non spécifié"),
            "university":       sch.get("university", "Non spécifié"),
            "country":          sch.get("country", "Non spécifié"),
            "level":            sch.get("level", []),
            "field_of_study":   sch.get("field_of_study", []),
            "funding_type":     sch.get("funding_type", "Non spécifié"),
            "award":            f"{sch.get('award', 'N/A')} {sch.get('currency', '')}".strip(),
            "deadline":         sch.get("deadline", "Non spécifié"),
            "status":           sch.get("status", ""),
            "gpa_min":          (sch.get("eligibility") or {}).get("GPA_min"),
            "application_link": sch.get("application_link", "Non spécifié"),
            "popularity_score": sch.get("popularity_score"),
            "score":            score,
        })

    return {"scholarships": result}
