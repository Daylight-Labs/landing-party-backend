from .timestamped_deletable_model import TimeStampedDeletableModel
from django.db import models
from api.models import User, QaDocument, Community

EVENT_TYPE_QUESTION_WITH_DIRECT_ANSWER = "QUESTION_WITH_DIRECT_ANSWER"
EVENT_TYPE_QUESTION_WITH_POTENTIAL_ANSWERS = "QUESTION_WITH_POTENTIAL_ANSWERS"
EVENT_TYPE_QUESTION_WITHOUT_ANSWER = "QUESTION_WITHOUT_ANSWER"
EVENT_TYPE_QUESTION_PROCESSING_RUNTIME_ERROR = "QUESTION_PROCESSING_RUNTIME_ERROR"

class EventLog(TimeStampedDeletableModel):
    id = models.AutoField(primary_key=True)

    type = models.TextField(choices=[
        (EVENT_TYPE_QUESTION_WITH_DIRECT_ANSWER, EVENT_TYPE_QUESTION_WITH_DIRECT_ANSWER),
        (EVENT_TYPE_QUESTION_WITH_POTENTIAL_ANSWERS, EVENT_TYPE_QUESTION_WITH_POTENTIAL_ANSWERS),
        (EVENT_TYPE_QUESTION_WITHOUT_ANSWER, EVENT_TYPE_QUESTION_WITHOUT_ANSWER),
        (EVENT_TYPE_QUESTION_PROCESSING_RUNTIME_ERROR, EVENT_TYPE_QUESTION_PROCESSING_RUNTIME_ERROR)
    ])

    community = models.ForeignKey(Community, on_delete=models.SET_NULL,
                                  to_field="guild_id",
                                  related_name="event_logs",
                                  null=True)

    triggered_by_user = models.ForeignKey(User, to_field="discord_user_id",
        null=True, on_delete=models.SET_NULL, related_name="triggered_event_logs")

    user_prompt = models.TextField(null=True)

    bot_response = models.TextField(null=True)

    slackbot_log = models.TextField(null=True)

    related_qa_document = models.ForeignKey(QaDocument,
        null=True, on_delete=models.SET_NULL, related_name="related_event_logs")

    is_spam = models.BooleanField(null=False, default=False)