# 🎨 Background Removal API

API REST pour supprimer l'arrière-plan d'images en utilisant RemBG et FastAPI.

## 🚀 Installation

### Prérequis
- Python 3.11+ (éviter 3.12 pour compatibilité avec numba)
- pip

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd rembg-api

# 2. Créer un environnement virtuel
python3.11 -m venv venv_rembg

# 3. Activer l'environnement
# Sur macOS/Linux :
source venv_rembg/bin/activate
# Sur Windows :
# venv_rembg\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt
```

## 🏃 Lancement du serveur

### Méthode 1 : Avec uvicorn (recommandé pour développement)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Paramètres expliqués :**
- `app.main:app` : Chemin vers l'instance FastAPI (fichier `app/main.py`, variable `app`)
- `--reload` : Recharge automatiquement le code lors des modifications
- `--host 0.0.0.0` : Écoute sur toutes les interfaces réseau (accessible depuis d'autres machines)
- `--port 8000` : Port HTTP à utiliser

### Méthode 2 : Directement avec Python
```bash
python -m app.main
```

### Méthode 3 : Pour production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
- `--workers 4` : Lance 4 processus workers pour gérer plus de requêtes simultanées

## 📚 Documentation

Une fois le serveur lancé, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

## 🔌 Endpoints disponibles

### 1. POST `/api/v1/remove-background` - Upload base64

**Description :** Supprime l'arrière-plan d'une image fournie en base64.

**Request Body (JSON) :**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "output_format": "base64",
  "post_process": true
}
```

**Paramètres :**
- `image_base64` (string, obligatoire) : Image encodée en base64
- `output_format` (string, optionnel) : Format de sortie (`base64`, `binary`, `url`)
- `post_process` (boolean, optionnel) : Active l'alpha matting pour des bords plus nets (défaut: `true`)

**Response (200 OK) :**
```json
{
  "success": true,
  "output_format": "base64",
  "image_data": "iVBORw0KGg...",
  "processing_time": 2.35,
  "original_size": [800, 600],
  "message": "Image traitée avec succès"
}
```

**Exemple avec curl :**
```bash
curl -X POST "http://localhost:8000/api/v1/remove-background" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'"$(base64 -i image.jpg)"'",
    "output_format": "base64",
    "post_process": true
  }'
```

**Exemple avec Python :**
```python
import requests
import base64

# Lire et encoder l'image
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

# Appeler l'API
response = requests.post(
    "http://localhost:8000/api/v1/remove-background",
    json={
        "image_base64": image_base64,
        "output_format": "base64",
        "post_process": True
    }
)

# Décoder et sauvegarder le résultat
if response.status_code == 200:
    result = response.json()
    output_image = base64.b64decode(result["image_data"])
    
    with open("output.png", "wb") as f:
        f.write(output_image)
    
    print(f"Traité en {result['processing_time']}s")
```

---

### 2. POST `/api/v1/remove-background-file` - Upload fichier

**Description :** Supprime l'arrière-plan d'un fichier image uploadé. Retourne l'image en binaire PNG.

**Request Body (multipart/form-data) :**
- `file` (file, obligatoire) : Fichier image à traiter
- `post_process` (boolean, optionnel) : Active l'alpha matting (défaut: `true`)

**Response (200 OK) :**
- Content-Type: `image/png`
- Body : Image PNG en binaire avec transparence

**Exemple avec curl :**
```bash
curl -X POST "http://localhost:8000/api/v1/remove-background-file" \
  -F "file=@image.jpg" \
  -F "post_process=true" \
  --output result.png
```

**Exemple avec Python :**
```python
import requests

# Uploader l'image
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/remove-background-file",
        files={"file": f},
        data={"post_process": "true"}
    )

# Sauvegarder le résultat
if response.status_code == 200:
    with open("output.png", "wb") as f:
        f.write(response.content)
    
    # Temps de traitement dans les headers
    print(f"Traité en {response.headers.get('X-Processing-Time')}s")
```

---

### 3. GET `/api/v1/health` - Health check

**Description :** Vérifie que le service est opérationnel.

**Response (200 OK) :**
```json
{
  "status": "healthy",
  "service": "background-removal-api",
  "version": "1.0.0"
}
```

**Exemple avec curl :**
```bash
curl http://localhost:8000/api/v1/health
```

## 📊 Formats supportés

### Formats d'entrée acceptés
- PNG
- JPEG / JPG
- WEBP
- BMP

### Formats de sortie
- **base64** : Image encodée en base64 (retournée dans le JSON)
- **binary** : Image PNG en binaire (uniquement avec `/remove-background-file`)
- **url** : URL vers S3 (non implémenté, retourne erreur 501)

## 🔧 Configuration avancée

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Limites
MAX_IMAGE_SIZE=16777216  # 16 mégapixels
MAX_FILE_SIZE=10485760   # 10 MB

# Logging
LOG_LEVEL=INFO
```

### Limites par défaut
- **Taille maximale** : 16 mégapixels (4096x4096)
- **Dimensions minimales** : 10x10 pixels
- **Timeout** : 30 secondes par requête

## 🧪 Tests

### Lancer les tests
```bash
pytest tests/ -v
```

### Tester manuellement avec Swagger
1. Ouvrez http://localhost:8000/docs
2. Cliquez sur l'endpoint `/api/v1/remove-background-file`
3. Cliquez sur "Try it out"
4. Uploadez une image
5. Cliquez sur "Execute"

## 📁 Structure du projet

```
rembg-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI principale
│   ├── routers/
│   │   ├── __init__.py
│   │   └── background.py    # Routes de traitement d'image
│   ├── services/
│   │   ├── __init__.py
│   │   └── image_processor.py  # Logique métier RemBG
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Modèles Pydantic
│   └── utils/
│       └── __init__.py
├── tests/
├── venv_rembg/
├── requirements.txt
└── README.md
```

## 🐛 Résolution des problèmes

### Erreur : "numba compatibility issue"
- **Cause** : Python 3.12 a des problèmes avec numba
- **Solution** : Utilisez Python 3.11

```bash
deactivate
rm -rf venv_rembg
python3.11 -m venv venv_rembg
source venv_rembg/bin/activate
pip install -r requirements.txt
```

### Erreur : "No module named 'app'"
- **Cause** : Le module `app` n'est pas dans le PYTHONPATH
- **Solution** : Lancez depuis la racine du projet

```bash
# Depuis la racine du projet
uvicorn app.main:app --reload
```

### L'API est lente
- **Causes possibles** :
  - Grandes images (>2000x2000)
  - CPU lent (RemBG est intensif)
  - Post-processing activé

- **Solutions** :
  - Redimensionner les images avant traitement
  - Désactiver `post_process` pour être plus rapide
  - Utiliser un GPU (installer `onnxruntime-gpu`)

## 📈 Performance

### Temps de traitement moyens
- Image 800x600 : ~2-3 secondes (CPU)
- Image 1920x1080 : ~5-8 secondes (CPU)
- Image 4000x3000 : ~15-25 secondes (CPU)

### Optimisations possibles
1. **Utiliser un GPU** : 3-5x plus rapide
2. **Caching** : Stocker les résultats pour éviter de retraiter
3. **Queue système** : Celery + Redis pour traitement asynchrone
4. **Redimensionnement** : Réduire les grandes images avant traitement

## 🔒 Sécurité

### Pour la production
1. **Limiter les origines CORS** :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://monsite.com"],  # Pas "*"
    ...
)
```

2. **Ajouter l'authentification** :
```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@router.post("/remove-background")
async def remove_bg(api_key: str = Depends(api_key_header)):
    # Vérifier api_key
    ...
```

3. **Rate limiting** : Utiliser slowapi ou middleware personnalisé

4. **Validation stricte** : Vérifier le type MIME réel des fichiers

## 📝 Licence

MIT

## 👨‍💻 Auteur

Votre nom