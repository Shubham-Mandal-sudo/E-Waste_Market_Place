import os
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

# Unique filename generator for product images
def product_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('product_images/', filename)

class EWasteItem(models.Model):
    LISTING_TYPES = [
        ('FIXED', 'Fixed Price'),
        ('AUCTION', 'Auction'),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=product_image_path)
    
    # Physical specs for transport calculation
    weight_kg = models.FloatField(help_text="Approximate weight in KG")
    pickup_pincode = models.CharField(max_length=6)

    # Listing Details
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPES, default='FIXED')
    
    # Pricing
    # For Fixed: This is the selling price.
    # For Auction: This is the Starting Bid.
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Auction Specifics
    buyout_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    auction_end_time = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_auction_active(self):
        if self.listing_type == 'FIXED':
            return False
        return not self.is_sold and self.auction_end_time > timezone.now()