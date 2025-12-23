from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from .models import EWasteItem

@login_required
def create_listing(request):
    # Only Sellers can list items
    if not request.user.is_seller:
        messages.error(request, "Only registered sellers can list items.")
        return redirect('home')

    if request.method == 'POST':
        # 1. Fetch Data
        title = request.POST.get('title')
        description = request.POST.get('description')
        weight = request.POST.get('weight')
        pincode = request.POST.get('pincode')
        listing_type = request.POST.get('listing_type') # 'FIXED' or 'AUCTION'
        base_price = request.POST.get('base_price')
        
        # File
        image = request.FILES.get('image')

        # 2. Basic Validation
        if not all([title, weight, base_price, image, listing_type]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'market/create_listing.html')

        # 3. Create Item Instance
        item = EWasteItem(
            seller=request.user,
            title=title,
            description=description,
            weight_kg=weight,
            pickup_pincode=pincode,
            listing_type=listing_type,
            base_price=base_price,
            image=image
        )

        # 4. Handle Auction Logic
        if listing_type == 'AUCTION':
            buyout_price = request.POST.get('buyout_price')
            end_date_str = request.POST.get('end_date') # Format from HTML: YYYY-MM-DDTHH:MM

            if not end_date_str:
                messages.error(request, "Auction items must have an end date.")
                return render(request, 'market/create_listing.html')
            
            # Parse Date
            try:
                end_time = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                # Make it timezone aware (important for Django)
                end_time = timezone.make_aware(end_time)
            except ValueError:
                messages.error(request, "Invalid date format.")
                return render(request, 'market/create_listing.html')

            # Validate Max 30 Days
            max_date = timezone.now() + timedelta(days=30)
            if end_time > max_date:
                messages.error(request, "Auctions cannot last longer than 30 days.")
                return render(request, 'market/create_listing.html')
            
            if end_time < timezone.now():
                messages.error(request, "End time cannot be in the past.")
                return render(request, 'market/create_listing.html')

            item.buyout_price = buyout_price if buyout_price else None
            item.auction_end_time = end_time

        item.save()
        messages.success(request, "Item listed successfully!")
        return redirect('seller_dashboard')

    return render(request, 'market/create_listing.html')

@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        return redirect('home')
    
    my_items = EWasteItem.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'market/seller_dashboard.html', {'items': my_items})