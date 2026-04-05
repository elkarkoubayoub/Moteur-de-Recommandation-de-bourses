
import json
from datetime import date

# ─── Profil de l'étudiant ────────────────────────────────────────────────────
PROFILE = {
    "level":          "master",
    "field":          "computer science",
    "nationality":    "morocco",
    "gpa":            3.5,
    "target_country": "usa",
}

# ─── Pondération des pays ─────────────────────────────────────────────────────
COUNTRY_WEIGHTS = {
    "usa":            0.30,  # 30 pts
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
    "international":  0.19,
}

TODAY = date.today()

# ─── 1. Charger la base ───────────────────────────────────────────────────────
with open("scholarships_dataset.json", encoding="utf-8") as f:
    all_scholarships = json.load(f)

# ─── 2. Filtre dur ───────────────────────────────────────────────────────────
def hard_filter(sch, profile):
    # (a) Pays cible = USA
    country = sch.get("country", "").strip().lower()
    if profile["target_country"].lower() not in country:
        return False, "Pays ≠ USA"

    # (b) Niveau = Master
    levels = [l.lower() for l in sch.get("level", [])]
    if profile["level"].lower() not in levels:
        return False, "Niveau non correspondant"

    # (c) GPA ≥ required minimum
    gpa_min = sch.get("eligibility", {}).get("GPA_min", 0) or 0
    if profile["gpa"] < gpa_min:
        return False, f"GPA insuffisant (requis ≥ {gpa_min})"

    # (d) Statut ouvert
    if sch.get("status", "").lower() != "open":
        return False, "Bourse fermée (closed)"

    return True, "OK"

# ─── 3. Calcul du score ──────────────────────────────────────────────────────
def compute_score(sch, profile):
    score = 0
    details = []

    # Niveau : 25 pts
    levels = [l.lower() for l in sch.get("level", [])]
    if profile["level"].lower() in levels:
        score += 25
        details.append("✅ Niveau Master : +25 pts")

    # Domaine d'étude : 25 pts
    field_student = profile["field"].lower()
    fields_sch = [f.lower() for f in sch.get("field_of_study", [])]
    field_match = any(field_student in f or f in ("all fields",) for f in fields_sch)
    if field_match:
        score += 25
        details.append("✅ Domaine CS correspondant : +25 pts")

    # Pays cible — pondération USA = 0.30 → 30 pts
    target = profile["target_country"].lower()
    country_sch = sch.get("country", "").lower()
    if target in country_sch:
        pts = int(COUNTRY_WEIGHTS.get(target, 0.20) * 100)
        score += pts
        details.append(f"✅ Pays cible USA (0.30×100) : +{pts} pts")

    # GPA : 15 pts
    gpa_min = sch.get("eligibility", {}).get("GPA_min", 0) or 0
    if profile["gpa"] >= gpa_min:
        score += 15
        details.append(f"✅ GPA {profile['gpa']} ≥ {gpa_min} : +15 pts")

    # Popularité : +5 pts si > 85
    pop = sch.get("popularity_score", 0) or 0
    if pop > 85:
        score += 5
        details.append(f"✅ Popularité {pop} > 85 : +5 pts")

    return min(score, 100), details

# ─── 4. Appliquer les filtres ─────────────────────────────────────────────────
results = []
rejected = []

for sch in all_scholarships:
    ok, reason = hard_filter(sch, PROFILE)
    if ok:
        score, details = compute_score(sch, PROFILE)
        results.append({
            "id":       sch["id"],
            "title":    sch["title"],
            "country":  sch["country"],
            "level":    sch.get("level"),
            "field":    sch.get("field_of_study"),
            "award":    f"{sch.get('award', 'N/A')} {sch.get('currency', '')}",
            "deadline": sch.get("deadline"),
            "status":   sch.get("status"),
            "gpa_min":  sch.get("eligibility", {}).get("GPA_min"),
            "link":     sch.get("application_link"),
            "score":    score,
            "details":  details,
        })
    else:
        rejected.append({"id": sch["id"], "title": sch["title"],
                         "reason": reason, "country": sch.get("country")})

results.sort(key=lambda x: x["score"], reverse=True)

# ─── 5. Affichage ─────────────────────────────────────────────────────────────
SEPARATOR = "─" * 68

print(f"\n{'═'*68}")
print(f"  🎓  MOTEUR DE RECOMMANDATION DE BOURSES — SCHOLARLY")
print(f"{'═'*68}")
print(f"  Profil : {PROFILE['level'].capitalize()} | {PROFILE['field'].title()}")
print(f"           Nationalité : {PROFILE['nationality'].title()} | GPA : {PROFILE['gpa']}")
print(f"           Pays cible  : {PROFILE['target_country'].upper()}")
print(f"{'═'*68}\n")

print(f"  📋  ÉTAPE 1 — FILTRE DUR (critères obligatoires)")
print(f"  Critères appliqués :")
print(f"  • Pays cible       =  USA")
print(f"  • Niveau           =  Master")
print(f"  • GPA minimum      ≥  {PROFILE['gpa']}")
print(f"  • Statut           =  open")
print(SEPARATOR)
print(f"  {len(results)} bourse(s) passent les filtres / "
      f"{len(all_scholarships)} dans la base.\n")

if not results:
    print("  ❌  Aucune bourse ne correspond aux critères stricts.\n")
else:
    print(f"  📊  ÉTAPE 2 — CALCUL DU SCORE DE COMPATIBILITÉ")
    print(f"  Pondération pays (USA) : 0.30 × 100 = 30 pts max")
    print(f"  Barème total (max 100 pts) :")
    print(f"    • Niveau       : 25 pts")
    print(f"    • Domaine      : 25 pts")
    print(f"    • Pays (USA)   : 30 pts  ← coefficient 0.30")
    print(f"    • GPA ≥ min    : 15 pts")
    print(f"    • Popularité   :  5 pts (bonus si > 85)")
    print(SEPARATOR)
    print()

    for rank, r in enumerate(results, 1):
        print(f"  🏆  #{rank}  {r['title']}  [Score : {r['score']}/100]")
        print(f"      ID        : {r['id']}")
        print(f"      Pays      : {r['country']}")
        print(f"      Niveau(x) : {', '.join(r['level'])}")
        print(f"      Domaine   : {', '.join(r['field'])}")
        print(f"      Montant   : {r['award']}")
        print(f"      Deadline  : {r['deadline']}")
        print(f"      GPA min   : {r['gpa_min']}")
        print(f"      Statut    : ✅ {r['status'].upper()}")
        print(f"      Lien      : {r['link']}")
        print(f"      ── Détail score ──")
        for d in r["details"]:
            print(f"         {d}")
        print()

    # ─── Tableau récapitulatif ─────────────────────────────────────────────
    print(SEPARATOR)
    print(f"  📌  TABLEAU RÉCAPITULATIF – TOP {len(results)}")
    print(SEPARATOR)
    header = f"  {'#':<3} {'ID':<8} {'Titre':<40} {'Score':>6}"
    print(header)
    print(f"  {'-'*3} {'-'*8} {'-'*40} {'-'*6}")
    for rank, r in enumerate(results, 1):
        title_trunc = r["title"][:38] + ".." if len(r["title"]) > 38 else r["title"]
        print(f"  {rank:<3} {r['id']:<8} {title_trunc:<40} {r['score']:>5}/100")

print(f"\n{'═'*68}\n")
