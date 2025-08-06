from .models import Base

# Import all models to ensure they are registered with SQLAlchemy
from contactform.mission.models import Mission
from contactform.insertion.models import FormSubmission
from contactform.detection.models import ContactFormDetection

__all__ = ["Base", "Mission", "FormSubmission", "ContactFormDetection"]

__all__ = ["Base"]
