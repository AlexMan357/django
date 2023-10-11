from django import forms
from myauth.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "bio", "agreement_accepted", "avatar"