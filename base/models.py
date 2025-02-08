from django.db import models
from django.contrib.auth.models import AbstractUser


class Theme(models.Model):
    name=models.CharField(max_length=20)
    color1=models.CharField(max_length=10)
    color2=models.CharField(max_length=10)
    color3=models.CharField(max_length=10)
    def __str__(self):
        return self.name


class User(AbstractUser):
    name=models.CharField(max_length=20)
    username=models.CharField(max_length=20,unique=True,null=True)
    bio=models.CharField(max_length=50,null=True)
    friends=models.ManyToManyField('self',null=True,related_name='friendship',blank=True)
    image=models.ImageField(null=True,default='users/avatar.svg',upload_to='users/')
    theme=models.ForeignKey(Theme,null=True,blank=True,on_delete=models.NOT_PROVIDED)


class Group(models.Model):
    name=models.CharField(max_length=20)
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    description=models.CharField(max_length=100,null=True)
    participants=models.ManyToManyField(User,related_name='participants',blank=True)
    is_public=models.BooleanField()
    image=models.ImageField(null=True,default='groups/avatar.svg',upload_to='groups/')
    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class image_message(models.Model):
    image=models.ImageField(upload_to='images/')
    sender=models.IntegerField()
    receiver=models.IntegerField()
    seen = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.image}"


class group_image_message(models.Model):
    image=models.ImageField(upload_to='group_images/')
    sender=models.IntegerField()
    receiver=models.IntegerField()
    seen = models.ManyToManyField(User,null=True,related_name='image_seen')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.image}"


class message(models.Model):
    text=models.CharField(max_length=100)
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='image_sender')
    receiver=models.ForeignKey(User,on_delete=models.CASCADE,related_name='image_receiver')
    seen=models.CharField(max_length=10)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} : {self.text}"


class groupMessage(models.Model):
    text = models.CharField(max_length=100)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='g_sender')
    receiver=models.ForeignKey(Group,on_delete=models.CASCADE,related_name='g_receiver',null=True)
    seen = models.ManyToManyField(User,null=True,related_name='seen')
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)


class status(models.Model):
    time=models.DateTimeField(auto_now=True)
    user_id=models.IntegerField()


class Request(models.Model):
    user1=models.IntegerField()
    user2=models.IntegerField()

    def __str__(self):
        return f"{self.user1}->{self.user2}"