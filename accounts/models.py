import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Utility function to generate unique filenames
def recycler_doc_path(instance, filename):
    # 1. Get the extension (e.g., '.pdf', '.jpg')
    ext = filename.split('.')[-1]
    # 2. Generate a random UUID (e.g., 'a1b2c3d4-...')
    new_filename = f"{uuid.uuid4()}.{ext}"
    # 3. Return the full path (e.g., 'recycler_docs/a1b2c3d4-....pdf')
    return os.path.join('recycler_docs/', new_filename)

class User(AbstractUser):
    # Common fields for all users
    is_seller = models.BooleanField(default=False)
    is_recycler = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.username

class RecyclerProfile(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recycler_profile')
    company_name = models.CharField(max_length=100)
    
    # UPDATED: Now uses the function 'recycler_doc_path'
    registration_doc = models.FileField(upload_to=recycler_doc_path, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_count = models.IntegerField(default=0)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} - {self.status}"