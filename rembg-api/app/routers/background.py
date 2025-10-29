"""
Router pour les endpoints de suppression d'arrière-plan.

Ce module définit toutes les routes liées au traitement d'image.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import Response
from PIL import Image
import io
import logging

from app.models.schemas import (
    ImageProcessRequest,
    ImageProcessResponse,
    ErrorResponse,
    OutputFormat
)
from app.services.image_processor import image_service

# Configuration du logger
logger = logging.getLogger(__name__)

# Création du router
# APIRouter = sous-application FastAPI qu'on peut attacher à l'app principale
# prefix = préfixe pour toutes les routes de ce router
# tags = catégorie dans la doc Swagger
router = APIRouter(prefix="/api/v1", tags=["Background Removal"])



@router.post(
    "/remove-background",
    response_model=ImageProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Supprimer l'arrière-plan d'une image (base64)",
    description="""
    Supprime l'arrière-plan d'une image fournie en base64.
    
    **Formats supportés** : PNG, JPEG, JPG, WEBP, BMP
    
    **Limites** :
    - Taille maximale : 16 mégapixels
    - Dimensions minimales : 10x10 pixels
    
    **Paramètres** :
    - `image_base64` : Image encodée en base64 (obligatoire)
    - `output_format` : Format de sortie (base64, binary, url)
    - `post_process` : Active l'alpha matting pour des bords plus nets
    """,
    responses={
        200: {
            "description": "Image traitée avec succès",
            "model": ImageProcessResponse
        },
        400: {
            "description": "Requête invalide",
            "model": ErrorResponse
        },
        500: {
            "description": "Erreur serveur",
            "model": ErrorResponse
        }
    }
)
async def remove_background_base64(request: ImageProcessRequest):
    """
    Endpoint POST pour supprimer l'arrière-plan via base64.
    
    'async' = fonction asynchrone, permet de traiter plusieurs requêtes simultanément
    FastAPI gère automatiquement l'asynchronisme
    
    Args:
        request Modèle Pydantic contenant l'image base64 et les options

    Returns:
        ImageProcessResponse avec l'image traitée
        
    Raises:
        HTTPException: En cas d'erreur de validation ou de traitement
    """
    try:
        logger.info(f"Nouvelle requête de traitement - Format sortie: {request.output_format}")
        
        # Convertir base64 en Image PIL
        input_image = image_service.base64_to_image(request.image_base64)
        
        # Traiter l'image
        output_image, processing_time = image_service.remove_background(
            input_image,
            post_process=request.post_process
        )
        
        # Préparer la réponse selon le format demandé
        if request.output_format == OutputFormat.BASE64:
            # Convertir l'image en base64
            image_data = image_service.image_to_base64(output_image, format="PNG")
        
        elif request.output_format == OutputFormat.URL:
            # TODO: Uploader vers S3 et retourner l'URL
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Le format 'url' n'est pas encore implémenté. Utilisez 'base64' ou 'binary'."
            )
        
        else:  # BINARY
            # Pour binary, on va quand même retourner du base64 dans le JSON
            # L'endpoint séparé /remove-background-file gère le vrai binaire
            image_data = image_service.image_to_base64(output_image, format="PNG")
        
        # Construire et retourner la réponse
        return ImageProcessResponse(
            success=True,
            output_format=request.output_format,
            image_data=image_data,
            processing_time=round(processing_time, 3),
            original_size=input_image.size,
            message="Image traitée avec succès"
        )
        
    except ValueError as e:
        # Erreur de validation (image invalide, etc.)
        logger.error(f"Erreur de validation : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        # Erreur inattendue
        logger.error(f"Erreur de traitement : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de l'image : {str(e)}"
        )




@router.post(
    "/remove-background-file",
    status_code=status.HTTP_200_OK,
    summary="Supprimer l'arrière-plan d'une image (upload fichier)",
    description="""
    Supprime l'arrière-plan d'une image uploadée directement.
    
    **Retourne l'image en binaire PNG avec transparence.**
    
    **Formats supportés** : PNG, JPEG, JPG, WEBP, BMP
    """,
    responses={
        200: {
            "description": "Image PNG avec arrière-plan supprimé",
            "content": {"image/png": {}}
        },
        400: {
            "description": "Fichier invalide",
            "model": ErrorResponse
        }
    }
)
async def remove_background_file(
    file: UploadFile = File(..., description="Fichier image à traiter"),
    post_process: bool = False
):
    """
    Endpoint POST pour supprimer l'arrière-plan via upload de fichier.
    
    'UploadFile' = type FastAPI pour gérer les uploads multipart/form-data
    'File(...)' = indique que ce paramètre vient d'un formulaire
    
    Args:
        file: Fichier uploadé par l'utilisateur
        post_process: Active l'alpha matting
    
    Returns:
        Response contenant l'image PNG en binaire
    """
    try:
        logger.info(f"Upload de fichier : {file.filename} ({file.content_type})")
        
        # Lire le contenu du fichier
        # await = attend que l'opération asynchrone se termine
        contents = await file.read()
        
        # Convertir en Image PIL
        input_image = Image.open(io.BytesIO(contents))
        
        # Traiter l'image
        output_image, processing_time = image_service.remove_background(
            input_image,
            post_process=post_process
        )
        
        # Convertir en bytes PNG
        output_bytes = image_service.image_to_bytes(output_image, format="PNG")
        
        logger.info(f"Fichier traité en {processing_time:.2f}s")
        
        # Retourner l'image en tant que réponse binaire
        # Response = réponse HTTP personnalisée
        # media_type = type MIME (indique au client que c'est une image PNG)
        return Response(
            content=output_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=nobg_{file.filename}",
                "X-Processing-Time": str(round(processing_time, 3))
            }
        )
    
    except ValueError as e:
        logger.error(f"Erreur de validation : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Erreur de traitement : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement du fichier : {str(e)}"
        )



@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Vérifier l'état du service",
    description="Endpoint de santé pour vérifier que l'API est opérationnelle"
)
async def health_check():
    """
    Endpoint GET pour vérifier la santé du service.
    
    Returns:
        Statut du service
    """
    return {
        "status": "healthy",
        "service": "background-removal-api",
        "version": "1.0.0"
    }