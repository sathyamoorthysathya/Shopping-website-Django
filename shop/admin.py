from atexit import register
from django.contrib import admin
from PIL import Image
from.models import *

admin.site.register(Catagory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Favourite)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)
