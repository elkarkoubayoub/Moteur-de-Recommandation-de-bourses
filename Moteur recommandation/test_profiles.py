import json
from recommend import recommend

# Définition des 3 profils fictifs exigés pour valider la logique
profils = [
    {
        "nom": "Étudiant Marocain Master Info",
        "profil": {
            "level": "Master",
            "field": "Informatique",
            "target_country": "France",
            "gpa": 3.2,
            "country": "Maroc"
        }
    },
    {
        "nom": "Étudiant Africain PhD Sciences",
        "profil": {
            "level": "PhD",
            "field": "Sciences",
            "target_country": "USA",
            "gpa": 3.8,
            "country": "Senegal"
        }
    },
    {
        "nom": "Étudiant Européen Licence Droit",
        "profil": {
            "level": "Licence",
            "field": "Droit",
            "target_country": "UK",
            "gpa": 2.5,
            "country": "France"
        }
    }
]

if __name__ == "__main__":
    for p in profils:
        print(f"=== TEST : {p['nom']} ===")
        print("Profil JSON fourni :")
        print(json.dumps(p['profil'], indent=2, ensure_ascii=False))
        try:
            # Appel du moteur Python pur
            result = recommend(p['profil'], top_n=5)
            
            print("\nRésultats de Recommandations :")
            if "message" in result:
                # Gérer le cas où la liste est vide post-filtrage dur
                print(f"➜ {result['message']}")
            else:
                for idx, rec in enumerate(result.get("scholarships", [])):
                    print(f" {idx+1}. {rec['name']} ({rec['country']}) | Score: {rec['score']}/100")
                    print(f"    Montant: {rec['award']} | Deadline: {rec['deadline']}")
                    print(f"    Lien: {rec['application_link']}")
            print("\n" + "="*60 + "\n")
        except Exception as e:
            print(f"X Erreur survenue lors du calcul: {e}\n")
