from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from api.models.tag import Tag

class TagAdmin(admin.ModelAdmin):
    class Meta:
        model = Tag

    def qa_document_count(self, obj):
        return obj.qa_documents.count()

    list_display = [
        'id',
        'name',
        'community',
        'qa_document_count'
    ]

    fields = ['name', 'community', 'qa_documents']

admin.site.register(Tag, TagAdmin)