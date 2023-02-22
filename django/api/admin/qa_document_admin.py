from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
import csv
from django.db import transaction

from datetime import datetime

from api.models.qa_document import QaDocument, QaDocumentAlternativePrompt
from api.models.qa_document_completion_button import QaDocumentCompletionButton
from api.models.community import Community
from django.contrib.messages import constants as messages

from django.contrib.admin import SimpleListFilter

class CsvImportForm(forms.Form):
    guild_id = forms.CharField(required=True)
    csv_file = forms.FileField(required=True)

class UpdateGuildIdForm(forms.Form):
    current_guild_id = forms.CharField(required=True)
    new_guild_id = forms.CharField(required=True)

class QaDocumentCompletionButtonInlinne(admin.TabularInline):
    model = QaDocumentCompletionButton
    fields = ['label', 'button_style', 'triggered_flow']
    autocomplete_fields = ("triggered_flow",)

class QaDocumentAlternativePromptInlinne(admin.TabularInline):
    model = QaDocumentAlternativePrompt
    fields = ['alternative_prompt']

class QaDocumentGuildFilter(SimpleListFilter):
    title = 'Guild'
    parameter_name = 'guild'

    def lookups(self, request, model_admin):
        return [(c.guild_id, f"{c.guild_id} - {c.name}") for c in Community.objects.all()]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(guild_id=self.value())

class QaDocumentAdmin(admin.ModelAdmin):
    class Meta:
        model = QaDocument

    list_display = ['id', 'guild_id', 'prompt', 'completion']

    list_filter = (
        QaDocumentGuildFilter,
    )

    autocomplete_fields = ("asked_by", "answered_by", "last_edited_by")

    inlines = [QaDocumentCompletionButtonInlinne, QaDocumentAlternativePromptInlinne]

    def save_model(self, request, obj, form, change):
        obj.update_embedding_for_prompt()
        super().save_model(request, obj, form, change)

    exclude = ('model', 'embedding_vector', 'deleted_on')

    change_list_template = "entities/qa_document_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
            path('update-guild-id/', self.update_guild_id),
        ]
        return my_urls + urls
    
    def update_guild_id(self, request):
        if request.method == "POST":
            current_guild_id = request.POST['current_guild_id']
            new_guild_id = request.POST['new_guild_id']
            if not current_guild_id and new_guild_id:
                self.message_user(request, f'Guild ids must not be empty', level=messages.ERROR)    
                return redirect(".")

            number_of_updates = QaDocument.objects.filter(guild_id=current_guild_id).update(guild_id=new_guild_id)
            self.message_user(request, f'{number_of_updates} of QADocuments updates', level=messages.SUCCESS)    
            return redirect("..")            

        form = UpdateGuildIdForm()
        payload = {"form": form}
        return render(
            request, "entities/update_guild_id_form.html", payload
        )

    def import_csv(self, request):
        if request.method == "POST":
            guild_id = request.POST["guild_id"]

            if not Community.objects.filter(guild_id=guild_id).exists():
                self.message_user(request, f'Community with guild id {guild_id} does not exist')
                return redirect(".")

            file = request.FILES["csv_file"]
            decoded_file = list(map(lambda x: x + '\n', file.read().decode('utf-8').splitlines()))
            input_rows = list(csv.DictReader(decoded_file, skipinitialspace=True))

            VALID_PROMPT_NAMES = list(map(lambda x: x.lower(), ['Q', 'Qs', 'Question', 'Questions', 'Prompt', 'Prompts']))
            VALID_COMPLETION_NAMES = list(map(lambda x: x.lower(), ['A', "Answer", 'Answers', 'Completion', 'Completions']))

            validation_error = None
            prompt_column_name = None
            completion_column_name = None

            # Validation
            if len(input_rows) == 0:
                validation_error = f'Empty file'

            validated_data = []

            for i, row in enumerate(input_rows):
                if len(row) != 2:
                    validation_error = f'File should have exactly two columns. Actual: {len(row)}'
                    break
                if prompt_column_name is None:
                    valid_prompt_names = list(filter(lambda c: c.lower() in VALID_PROMPT_NAMES, row.keys()))
                    if len(valid_prompt_names) == 0:
                        validation_error = f'Prompt column not found'
                        break
                    prompt_column_name = valid_prompt_names[0]

                if completion_column_name is None:
                    valid_completion_names = list(filter(lambda c: c.lower() in VALID_COMPLETION_NAMES, row.keys()))
                    if len(valid_completion_names) == 0:
                        validation_error = f'Answer column not found'
                        break
                    completion_column_name = valid_completion_names[0]

                if prompt_column_name not in row:
                    validation_error = f'Prompt column not found in row {i + 1}'
                    break

                if completion_column_name not in row:
                    validation_error = f'Completion column not found in row {i + 1}'
                    break

                prompt = row[prompt_column_name]
                completion = row[completion_column_name]

                if not (isinstance(prompt, str) and isinstance(completion, str)):
                    validation_error = f'Value in row {i + 1} is not string'
                    break

                if len(prompt) > 2000:
                    validation_error = f'Prompt too long in row {i + 1}. Maximum length: 2000'
                    break

                if len(completion) > 20000:
                    validation_error = f'Answer too long in row {i + 1}. Maximum length: 20000'
                    break

                validated_data.append( (prompt, completion) )

            if validation_error:
                self.message_user(request, validation_error)
                return redirect(".")

            try:
                with transaction.atomic():
                    for (prompt, completion) in validated_data:
                        QaDocument.objects.filter(
                            prompt=prompt,
                            guild_id=guild_id
                        ).update(deleted_on=datetime.now())
                        qa_doc = QaDocument(
                            prompt=prompt,
                            completion=completion,
                            guild_id=guild_id
                        )
                        qa_doc.update_embedding_for_prompt()
                        qa_doc.save()
            except Exception as e:
                self.message_user(request, str(e))
                return redirect(".")

            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "entities/csv_form.html", payload
        )

admin.site.register(QaDocument, QaDocumentAdmin)