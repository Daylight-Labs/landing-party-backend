
from api.models import OnboardingFlowCreationObject, FaqBotCreationObject

def get_or_create_ftux_onboarding_obj(user):
    obj = OnboardingFlowCreationObject.objects.filter(creator=user).first()

    if obj is None:
        return OnboardingFlowCreationObject.objects.create(creator=user)

    return obj

def get_or_create_new_onboarding_obj(user):
    obj = OnboardingFlowCreationObject.objects.filter(flow__isnull=True, creator=user).first()

    if obj is None:
        return OnboardingFlowCreationObject.objects.create(creator=user)

    return obj

def get_or_create_new_faq_bot_obj(user):
    obj = FaqBotCreationObject.objects.filter(creator=user, is_completed=False).first()

    if obj is None:
        return FaqBotCreationObject.objects.create(creator=user, channel_ids=[])

    return obj