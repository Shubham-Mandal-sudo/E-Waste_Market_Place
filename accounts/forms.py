from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('seller', 'Seller (I want to sell E-Waste)'),
        ('recycler', 'Recycler (I want to buy E-Waste)'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    phone_number = forms.CharField(max_length=15, required=True)
    pincode = forms.CharField(max_length=6, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'pincode',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        
        if user_type == 'seller':
            user.is_seller = True
        elif user_type == 'recycler':
            # Note: We don't set is_recycler=True yet. 
            # They need admin approval first.
            user.is_recycler = False 
            
        if commit:
            user.save()
        return user