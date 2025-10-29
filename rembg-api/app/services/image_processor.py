"""
Service de traitement d'image pour la suppression d'arrière-plan.

Ce module contient toute la logique de traitement d'image,
isolée des détails de l'API (routes, HTTP, etc.).
"""

import io
import base64
import time
from typing import Tuple, Optional
from PIL import Image
from rembg import remove
import logging

# Configuration du logger pour le débogage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessingService:
    """
    Service responsable du traitement des images.
    
    Pattern de conception : Classe de service (Service Layer Pattern)
    Avantages : 
    - Réutilisable dans différentes routes
    - Facile à tester unitairement
    - Logique métier séparée de la logique HTTP
    """
    
    # Formats d'image supportés
    SUPPORTED_FORMATS = {'PNG', 'JPEG', 'JPG', 'WEBP', 'BMP'}
    
    # Taille maximale d'image (en pixels)
    MAX_IMAGE_SIZE = 4096 * 4096  # 16 mégapixels
    
    def __init__(self):
        """
        Constructeur du service.
        
        __init__ est appelé automatiquement lors de la création d'une instance.
        Ici, on pourrait précharger le modèle RemBG pour optimiser les performances.
        """
        logger.info("ImageProcessingService initialisé")
    
    @staticmethod
    def validate_image(image: Image.Image) -> Tuple[bool, Optional[str]]:
        """
        Valide qu'une image est acceptable pour le traitement.

        @staticmethod = méthode qui n'utilise pas 'self', donc peut être
                        appelée sans créer d'instance de la classe

        Args:
            image: Image PIL à valider

        Returns:
            Tuple (is_valid, error_message)
            - is_valid: True si l'image est valide
            - error_message: Message d'erreur si invalide, None sinon
        """
        # Vérifier le format (si disponible - peut être None après copy())
        if image.format is not None and image.format not in ImageProcessingService.SUPPORTED_FORMATS:
            return False, f"Format {image.format} non supporté. Formats acceptés : {ImageProcessingService.SUPPORTED_FORMATS}"

        # Vérifier la taille
        width, height = image.size
        if width * height > ImageProcessingService.MAX_IMAGE_SIZE:
            return False, f"Image trop grande ({width}x{height}). Maximum : {ImageProcessingService.MAX_IMAGE_SIZE} pixels"

        # Vérifier les dimensions minimales
        if width < 10 or height < 10:
            return False, "Image trop petite (minimum 10x10 pixels)"

        return True, None
    
    def remove_background(
        self,
        input_image: Image.Image,
        post_process: bool = False
    ) -> Tuple[Image.Image, float]:
        """
        Supprime l'arrière-plan d'une image.

        Args:
            input_image: Image PIL en entrée
            post_process: Appliquer le post-traitement alpha matting (default: False pour correspondre au notebook)

        Returns:
            Tuple (output_image, processing_time)
            - output_image: Image PIL avec arrière-plan transparent
            - processing_time: Temps de traitement en secondes

        Raises:
            ValueError: Si l'image n'est pas valide
            Exception: Si le traitement échoue
        """
        # Valider l'image
        is_valid, error_msg = self.validate_image(input_image)
        if not is_valid:
            logger.error(f"Validation échouée : {error_msg}")
            raise ValueError(error_msg)

        logger.info(f"Traitement d'une image {input_image.size} - Format: {input_image.format}")

        # Mesurer le temps de traitement
        start_time = time.time()

        try:
            # Appel à RemBG pour supprimer l'arrière-plan
            # Correspond exactement à l'usage du notebook: remove(img)
            if post_process:
                # Seulement si explicitement demandé
                output_image = remove(
                    input_image,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=240,
                    alpha_matting_background_threshold=10,
                    alpha_matting_erode_size=10
                )
            else:
                # Comportement par défaut identique au notebook
                output_image = remove(input_image)

            processing_time = time.time() - start_time
            logger.info(f"Traitement réussi en {processing_time:.2f}s")

            return output_image, processing_time

        except Exception as e:
            logger.error(f"Erreur lors du traitement : {str(e)}")
            raise Exception(f"Échec du traitement d'image : {str(e)}")
    
    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """
        Convertit une image PIL en chaîne base64.
        
        Base64 = encodage qui convertit des données binaires en texte
        Utile pour transférer des images via JSON
        
        Args:
            image: Image PIL à convertir
            format: Format de sortie (PNG, JPEG, etc.)
        
        Returns:
            Chaîne base64 de l'image
        """
        # Créer un buffer en mémoire (comme un fichier virtuel)
        buffer = io.BytesIO()
        
        # Sauvegarder l'image dans le buffer
        image.save(buffer, format=format)
        
        # Récupérer les bytes du buffer
        image_bytes = buffer.getvalue()
        
        # Encoder en base64
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        return base64_string
    
    @staticmethod
    def base64_to_image(base64_string: str) -> Image.Image:
        """
        Convertit une chaîne base64 en image PIL.
        
        Args:
            base64_string: Chaîne base64 représentant une image
        
        Returns:
            Image PIL
        
        Raises:
            ValueError: Si le base64 est invalide ou ne représente pas une image
        """
        try:
            # Décoder le base64 en bytes
            image_bytes = base64.b64decode(base64_string)
            
            # Créer un buffer à partir des bytes
            buffer = io.BytesIO(image_bytes)
            
            # Ouvrir l'image avec PIL
            image = Image.open(buffer)
            
            # Charger l'image en mémoire (évite les erreurs lazy-loading)
            image.load()
            
            return image
        
        except Exception as e:
            logger.error(f"Erreur de conversion base64 → image : {str(e)}")
            raise ValueError(f"Impossible de convertir le base64 en image : {str(e)}")
    
    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        """
        Convertit une image PIL en bytes bruts.
        
        Args:
            image: Image PIL à convertir
            format: Format de sortie
        
        Returns:
            Bytes de l'image
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()


# Instance singleton du service (créée une seule fois)
# Singleton = pattern où on crée une seule instance partagée
image_service = ImageProcessingService()