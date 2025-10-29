"""
Point d'entrée principal de l'API FastAPI.

Ce fichier initialise l'application et configure tous les middlewares,
routers, et options globales.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging

from app.routers import background

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


#Création de l'applicaiton FastAPI
# fastAPI() est l'instance principale de l'application
app = FastAPI(
    title="Background Removal API",
    description="""
    API REST pour supprimer l'arrière-plan d'images en utilisant RemBG.
    
    **Fonctionnalités** :
    - Suppression d'arrière-plan avec RemBG
    - Support de plusieurs formats d'image (PNG, JPEG, WEBP, etc.)
    - Deux modes d'upload : base64 ou fichier
    - Post-traitement optionnel pour des bords nets
    
    **Endpoints principaux** :
    - `POST /api/v1/remove-background` : Upload base64
    - `POST /api/v1/remove-background-file` : Upload fichier
    - `GET /api/v1/health` : Health check
    """,
    version="1.0.0",
    docs_url="/docs",    # URL de la documentation Swagger UI
    redoc_url="/redoc",    # URL de la documentation ReDoc 
    openapi_url="/openapi.json"   # URL duu schéma OpenAPI   
)

# Configuration CORS (Cross-Origin Resource Sharing)
# Permet à des applications web sur d'autres domaines d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)

# Enregistrement du router
# include router permet d'ajouter toutes les routes du router à l'application
app.include_router(background.router)

# Event handlers : fonctions appelées au démarrage/arrêt de l'application
@app.on_event("startup")
async def startup_event():
    """
    Exécuté au démarrage de l'application.
    
    Utile pour :
    - Précharger des modèles ML
    - Établir des connexions à la base de données
    - Initialiser des caches
    """
    logger.info("🚀 Démarrage de l'API Background Removal")
    logger.info("📚 Documentation disponible sur : http://localhost:8000/docs")
    
    
app.on_event("shutdown")
async def shutdown_event():
    """
    Exécuté à l'arrêt de l'application.
    
    Utile pour :
    - Fermer les connexions à la base de données
    - Nettoyer les ressources
    - Sauvegarder l'état
    """
    logger.info("🛑 Arrêt de l'API Background Removal")
    
    
#Route racine :  redirige vers la documentation
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Exemple de middleware personnalisé (optionnel)
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware qui log chaque requête.
    
    Middleware = fonction qui s'exécute avant/après chaque requête
    call_next = fonction qui appelle le prochain middleware ou la route
    
    Args:
        request: Requête HTTP entrante
        call_next: Fonction pour passer à l'étape suivante
    
    Returns:
        Réponse HTTP
    """
    # Avant la requête
    logger.info(f"📨 {request.method} {request.url.path}")
    
    # Traiter la requête
    response = await call_next(request)
    
    # Après la requête
    logger.info(f"✅ {request.method} {request.url.path} - Status: {response.status_code}")
    
    return response

# Point d'entrée pour lancer l'application directement avec Python
# Alternative à uvicron en ligne de commande

if __name__== "__main__":
    import uvicorn
    
    # uvicorn.run() =. lance le serveru ASGI
    uvicorn.run(
                "app:main:app",                                 # Chemin vers l'application (module: variable)
                host="0.0.0.0",                                 # Écoute sur toutes les interfaces réseau
                port=8000,                                      # Port HTTP
                reload= True ,                                   # Recharge automatiquement lors des changements de code
                log_level="info"
                )




