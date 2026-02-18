from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Hermano)
admin.site.register(Rol)
admin.site.register(HermanoRol)
admin.site.register(TipoCulto)
admin.site.register(Culto)

