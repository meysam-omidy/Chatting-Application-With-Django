from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,Group, image_message, group_image_message


class myUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['name','username','password1','password2']

class profileForm(ModelForm):
    class Meta:
        model=User
        fields=['name','username','bio','image']

class groupCreationForm(ModelForm):
    class Meta:
        model=Group
        fields=['name','description','image','is_public']

class imageForm(ModelForm):
    class Meta:
        model=image_message
        fields=['image','sender','receiver']

class groupImageForm(ModelForm):
    class Meta:
        model=group_image_message
        fields=['image','sender','receiver']

