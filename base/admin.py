from django.contrib import admin
from .models import User,Group,message,groupMessage,status,Request,Theme, image_message, group_image_message
# Register your models here.

admin.site.register(User)
admin.site.register(Group)
admin.site.register(message)
admin.site.register(groupMessage)
admin.site.register(status)
admin.site.register(Request)
admin.site.register(Theme)
admin.site.register(image_message)
admin.site.register(group_image_message)