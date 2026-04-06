from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    alt_phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    landmark = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=10)
    order_notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not phone.isdigit() or len(phone) != 10 or phone[0] not in '6789':
            raise forms.ValidationError('Enter a valid 10-digit Indian mobile number.')
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'state', 'pincode']
        widgets = {
            'phone': forms.TextInput(attrs={'style': 'width:100%; padding:0.8rem; border:1px solid #d7d8c9; border-radius:14px;'}),
            'address': forms.Textarea(attrs={'rows': 3, 'style': 'width:100%; padding:0.8rem; border:1px solid #d7d8c9; border-radius:14px;'}),
            'city': forms.TextInput(attrs={'style': 'width:100%; padding:0.8rem; border:1px solid #d7d8c9; border-radius:14px;'}),
            'state': forms.TextInput(attrs={'style': 'width:100%; padding:0.8rem; border:1px solid #d7d8c9; border-radius:14px;'}),
            'pincode': forms.TextInput(attrs={'style': 'width:100%; padding:0.8rem; border:1px solid #d7d8c9; border-radius:14px;'}),
        }
