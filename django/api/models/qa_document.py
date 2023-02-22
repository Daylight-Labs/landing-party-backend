from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models

import openai
import pickle

from api.models.user import User

API_ENGINE = "text-similarity-ada-001"

class QaDocumentAlternativePrompt(models.Model):
    qa_document = models.ForeignKey("QaDocument", on_delete=models.CASCADE, related_name="alternative_prompts",
                                    blank=False, null=False)
    alternative_prompt = models.TextField(blank=False)
    model = models.TextField(blank=False, default="text-similarity-ada-001")
    embedding_vector = models.BinaryField()

    def save(self, *args, **kwargs):
        if self.embedding_vector is None or len(self.embedding_vector) == 0:
            self.update_embedding_for_prompt()
        super(QaDocumentAlternativePrompt, self).save(*args, **kwargs)

    def update_embedding_for_prompt(self):
        embedding_response = openai.Embedding.create(input=self.alternative_prompt, engine=API_ENGINE)
        embedding = embedding_response['data'][0]['embedding']
        embedding_str = pickle.dumps(embedding)
        self.embedding_vector = embedding_str
        self.save()

class QaDocument(TimeStampedDeletableModel):
    id = models.AutoField(primary_key=True)

    guild_id = models.BigIntegerField(db_index=True)

    prompt = models.TextField(blank=False)
    completion = models.TextField(blank=False)

    asked_by = models.ForeignKey(User, to_field="discord_user_id",
                                 null=True, on_delete=models.SET_NULL, related_name="asked_qa_documents",
                                 blank=True)
    answered_by = models.ForeignKey(User, to_field="discord_user_id",
                                    null=True, on_delete=models.SET_NULL, related_name="answered_qa_documents",
                                    blank=True)

    question_jump_url = models.TextField(blank=True, null=True)
    answer_jump_url = models.TextField(blank=True, null=True)

    last_edited_by = models.ForeignKey(User, to_field="discord_user_id",
                                       null=True, on_delete=models.SET_NULL, related_name="edited_qa_questions",
                                       blank=True)

    is_public = models.BooleanField(null=False, default=False)

    model = models.TextField(blank=False, default="text-similarity-ada-001")
    embedding_vector = models.BinaryField()

    revision_date = models.DateTimeField(verbose_name="Revision Date", null=True, blank=True)

    is_spam = models.BooleanField(null=False, default=False,
                                  help_text="Used for kicking users for spamming (see 'Kick users after X spam messages within 7 days' field in community admin)")

    def update_embedding_for_prompt(self):
        embedding_response = openai.Embedding.create(input=self.prompt, engine=API_ENGINE)
        embedding = embedding_response['data'][0]['embedding']
        embedding_str = pickle.dumps(embedding)
        self.embedding_vector = embedding_str

        for alt_prompt in self.alternative_prompts.all():
            alt_prompt.update_embedding_for_prompt()

    def __str__(self):
        return f"[{self.guild_id}] {self.prompt[:100]}"

    def save(self, *args, **kwargs):
        if self.question_jump_url == "":
            self.question_jump_url = None
        if self.answer_jump_url == "":
            self.answer_jump_url = None
        super(QaDocument, self).save(*args, **kwargs)