import os
from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
from recommend import recommend
from cv_generator import generate_pdf_cv
from lm_generator import save_motivation_letter

app = Flask(__name__)
# Active CORS pour autoriser les requêtes provenant de Botpress (ou autre domaine)
CORS(app)

# Dossier où les fichiers générés (CV et LM) seront stockés
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """
    Endpoint: /recommend
    Reçoit un profil JSON de Botpress et retourne le Top 5 des bourses appropriées.
    """
    profile = request.get_json()
    if not profile:
        return jsonify({"error": "Le corps de la requête doit contenir un profil JSON valide."}), 400
        
    result = recommend(profile, top_n=5, dataset_path='scholarships_dataset.json')
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
        
    return jsonify(result), 200

@app.route('/generate-cv', methods=['POST'])
def create_cv():
    """
    Endpoint: /generate-cv
    Génère un CV en PDF à partir des données Botpress.
    Retourne l'URL pour télécharger le PDF.
    """
    cv_data = request.get_json()
    if not cv_data:
        return jsonify({"error": "Invalid request"}), 400
        
    user_name = cv_data.get('user_name', 'default').replace(' ', '_')
    filename = f"{user_name}_CV.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    generate_pdf_cv(cv_data, filepath)
    
    # Construit l'URL externe pour accéder au fichier
    file_url = url_for('download_file', filename=filename, _external=True)
    return jsonify({"message": "CV generated successfully", "url": file_url}), 200

@app.route('/generate-lm', methods=['POST'])
def create_lm():
    """
    Endpoint: /generate-lm
    Génère une lettre de motivation (texte) via AI / Template intelligent.
    """
    lm_data = request.get_json()
    if not lm_data:
        return jsonify({"error": "Invalid request"}), 400
        
    user_name = lm_data.get('user_name', 'default').replace(' ', '_')
    filename = f"{user_name}_Motivation_Letter.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    save_motivation_letter(lm_data, filepath)
    
    # Construit l'URL externe pour accéder au fichier
    file_url = url_for('download_file', filename=filename, _external=True)
    return jsonify({"message": "Motivation letter generated successfully", "url": file_url}), 200

@app.route('/outputs/<path:filename>', methods=['GET'])
def download_file(filename):
    """
    Sert les fichiers statiques (PDF générés, Lettres de motivation).
    """
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    # Lance le serveur Flask 
    # port 5000, accessible via les requêtes réseau
    app.run(host='0.0.0.0', port=5000, debug=True)


