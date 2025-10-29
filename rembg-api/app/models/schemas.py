"""
Modèles Pydantic pour la validation des données.

Pydantic valide automatiquement les données entrantes et sortantes,
et génère une documentation OpenAPI claire.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum


class OutputFormat(str, Enum):
    """
    Formats de sortie supportés pour l'image traitée.
    
    Enum = énumération, liste fixe de valeurs autorisées
    """
    BASE64 = "base64"      # Image encodée en base64 (texte)
    BINARY = "binary"      # Image en bytes bruts
    URL = "url"           # URL vers S3 (à implémenter)


class ImageProcessRequest(BaseModel):
    """
    Modèle pour la requête de traitement d'image avec base64.
    
    BaseModel = classe de base Pydantic qui ajoute la validation
    """
    image_base64: str = Field(
        ...,  # ... = champ obligatoire
        description="Image encodée en base64",
        example="iVBORw0KGgoAAAANSUhEUg..."
    )
    
    output_format: OutputFormat = Field(
        default=OutputFormat.BASE64,
        description="Format de sortie souhaité"
    )
    
    post_process: bool = Field(
        default=False,
        description="Appliquer le post-traitement alpha matting pour des bords plus nets (default: False pour correspondre au notebook)"
    )
    
    @validator('image_base64')
    def validate_base64(cls, v):
        """
        Validateur personnalisé pour vérifier que le base64 est valide.
        
        @validator = décorateur qui exécute cette fonction sur le champ
        cls = la classe (ImageProcessRequest)
        v = la valeur du champ à valider
        """
        import base64
        try:
            # Tenter de décoder pour valider
            base64.b64decode(v)
        except Exception:
            raise ValueError("Le base64 fourni est invalide")
        return v


class ImageProcessResponse(BaseModel):
    """
    Modèle pour la réponse de traitement d'image.
    """
    success: bool = Field(
        description="Indique si le traitement a réussi"
    )
    
    output_format: OutputFormat = Field(
        description="Format de l'image retournée"
    )
    
    image_data: Optional[str] = Field(
        default=None,
        description="Image encodée en base64 ou URL (selon output_format)"
    )
    
    processing_time: float = Field(
        description="Temps de traitement en secondes"
    )
    
    original_size: tuple[int, int] = Field(
        description="Dimensions de l'image originale (largeur, hauteur)"
    )
    
    message: Optional[str] = Field(
        default=None,
        description="Message d'information ou d'erreur"
    )
    
    class Config:
        """
        Configuration du modèle Pydantic.
        
        Cette classe interne configure le comportement de Pydantic.
        """
        json_schema_extra = {
            "example": {
                "success": True,
                "output_format": "base64",
                "image_data": "iVBORw0KGg...",
                "processing_time": 2.35,
                "original_size": [800, 600],
                "message": "Image traitée avec succès"
            }
        }


class ErrorResponse(BaseModel):
    """
    Modèle pour les réponses d'erreur standardisées.
    """
    success: bool = Field(default=False)
    error: str = Field(description="Type d'erreur")
    detail: str = Field(description="Détails de l'erreur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "InvalidImageFormat",
                "detail": "Le format d'image n'est pas supporté"
            }
        }