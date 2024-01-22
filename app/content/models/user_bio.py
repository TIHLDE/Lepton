from django.db import models

class UserBio(models.Model):
    
    user_bio_id = models.CharField(max_length=15, primary_key=True)

    role = models.CharField(max_length=50) #todo mulig at dette må endres til et velge-felt

    description = models.CharField(max_length=50)

    gitHub_link = models.URLField(max_length=300, blank=True, null=True)

    linkedIn_link = models.URLField(max_length=300, blank=True, null=True)
    