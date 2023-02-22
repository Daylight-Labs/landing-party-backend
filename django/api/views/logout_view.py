from rest_framework import views
from rest_framework.permissions import IsAuthenticated

class LogOutTokenView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=200)
        except Exception as e:
            return Response(status=400)
