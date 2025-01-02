from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import TherapistProfile

@receiver(post_save, sender=User)
def create_or_update_therapist_profile(sender, instance, created, **kwargs):
    """
    Automatically create or update a TherapistProfile for each User
    """
    # Check if a TherapistProfile already exists
    try:
        therapist_profile = TherapistProfile.objects.get(user=instance)
        # Update if needed
        if not therapist_profile.is_active:
            therapist_profile.is_active = True
            therapist_profile.save()
    except TherapistProfile.DoesNotExist:
        # Create a new TherapistProfile
        TherapistProfile.objects.create(
            user=instance, 
            is_active=True  # Default to active
        )
