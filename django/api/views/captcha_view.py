from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from django.core.files import File
from io import BytesIO

from api.models import CaptchaRequest, CaptchaFailuresCount, ShowCaptcha
from api.permissions.bot_api_permission import BotApiPermission
import os

import requests

from api.models import ShowCaptcha

from storages.backends.s3boto3 import S3Boto3Storage
from multicolorcaptcha import CaptchaGenerator

from io import BytesIO
from django.core.files.base import ContentFile

from api.serializers import CaptchaRequestSerializer
from rest_framework.permissions import AllowAny

API_CHATBOT_AUTH_TOKEN = os.environ['CHATBOT_API_AUTH_TOKEN']
ENVIRONMENT = os.environ['ENVIRONMENT']

@api_view(['POST'])
@permission_classes([AllowAny])
def create_captcha_challenge(request):
    captcha_type = request.data.get("captcha_type")
    if captcha_type is None:
        return JsonResponse(
            {"success": False, "error": f"captcha type is missing"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    CAPCTHA_SIZE_NUM = 2
    generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)

    captcha_challenge_text = None
    captcha_challenge_answer = None
    captcha_image = None
    if ShowCaptcha.CaptchaType.TEXT.value == captcha_type:
        text_captcha = generator.gen_captcha_image(difficult_level=3)
        captcha_image = text_captcha.image
        captcha_challenge_text = text_captcha.characters
        captcha_challenge_answer = text_captcha.characters
    else:
        math_captcha = generator.gen_math_captcha_image(difficult_level=1)
        captcha_image = math_captcha.image
        captcha_challenge_text = math_captcha.equation_str
        captcha_challenge_answer = math_captcha.equation_result
    
    r = CaptchaRequest(equation_string=captcha_challenge_text, equation_result=captcha_challenge_answer)
    r.save()

    f = BytesIO()
    captcha_image.save(f, format="png")
    r.image.save(f"{r.id}_{ENVIRONMENT}.png", ContentFile(f.getvalue()))
    r.save()

    serializer = CaptchaRequestSerializer(r)

    response = Response(serializer.data)
    return response

@api_view(['POST'])
def verify_captcha_challenge(request, request_id, discord_user_id):
    captcha_request = CaptchaRequest.objects.get(pk=request_id)

    if captcha_request is None:
        return JsonResponse(
            {"success": False, "error": f"Captcha request with id {request_id} does not exist"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    user_answer = request.data["answer"]
    if user_answer is None:
       return JsonResponse(
            {"success": False, "error": f"Missing answer in response body"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    captcha_failure_count = None
    try:
        captcha_failure_count = CaptchaFailuresCount.objects.get(discord_user_id=discord_user_id)
    except:
        pass

    if captcha_request.equation_result == user_answer:
        if captcha_failure_count:
            captcha_failure_count.failure_count = 0
            captcha_failure_count.save()

        return JsonResponse(
            {"success": True}, 
            status=status.HTTP_200_OK
        )
    else:
        if captcha_failure_count:
            captcha_failure_count.failure_count = captcha_failure_count.failure_count + 1
        else:
            captcha_failure_count = CaptchaFailuresCount(discord_user_id=discord_user_id, failure_count=1)
        captcha_failure_count.save()

        return JsonResponse(
            {"success": False, "error": f"Wrong captcha answer", "failure_count": captcha_failure_count.failure_count}, 
            status=status.HTTP_400_BAD_REQUEST
        )