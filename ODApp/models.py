from django.db import models

class Signupdb(models.Model):
    Username = models.CharField(max_length=50)
    Email = models.EmailField()
    Password = models.CharField(max_length=10)
    ConfirmPassword = models.CharField(max_length=10)

    class Meta:
        db_table = "odapp_signupdb"  # ✅ correct string (no comma)

class DetectionHistory(models.Model):
    user = models.CharField(max_length=50)
    input_file = models.FileField(upload_to='uploads/')
    output_file = models.FileField(upload_to='outputs/')
    detection_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "odapp_detectionhistory"
