from __future__ import unicode_literals
from django.contrib import admin
from .models import PortNode

# class NodeAdmin(admin.ModelAdmin):
#     list_display = ('name', )

admin.site.register(PortNode)

