from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, RecyclerProfile

def register(request):
    if request.method == 'POST':
        # 1. Fetch data manually from HTML inputs
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        user_type = request.POST.get('user_type') # 'seller' or 'recycler'

        # 2. Manual Validation
        errors = []
        if password != password_confirm:
            errors.append("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        
        if errors:
            return render(request, 'accounts/register.html', {'errors': errors, 'data': request.POST})

        # 3. Create User
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.phone_number = phone
            user.pincode = pincode
            
            if user_type == 'seller':
                user.is_seller = True
                user.save()
                login(request, user)
                return redirect('home')
            
            elif user_type == 'recycler':
                user.is_recycler = False # Not verified yet
                user.save()
                
                # Create the profile skeleton
                RecyclerProfile.objects.create(user=user)
                
                login(request, user)
                # Redirect recyclers immediately to document upload
                return redirect('upload_documents')

        except Exception as e:
            return render(request, 'accounts/register.html', {'errors': [str(e)]})

    return render(request, 'accounts/register.html')

@login_required
def upload_documents(request):
    # Ensure only recyclers access this
    try:
        profile = request.user.recycler_profile
    except RecyclerProfile.DoesNotExist:
        return redirect('home')

    # 3-Strike Rule Check
    if profile.rejection_count >= 3:
        return render(request, 'accounts/banned.html')

    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        # IMPORTANT: Files come from request.FILES
        doc = request.FILES.get('registration_doc')

        if not company_name or not doc:
            messages.error(request, "Please provide company name and document.")
        else:
            profile.company_name = company_name
            profile.registration_doc = doc
            profile.status = 'PENDING' # Reset status to pending if they re-apply
            profile.save()
            
            messages.success(request, "Documents uploaded successfully! Waiting for admin approval.")
            return redirect('home')

    return render(request, 'accounts/upload_doc.html', {'profile': profile})

def home(request):
    return render(request, 'home.html')