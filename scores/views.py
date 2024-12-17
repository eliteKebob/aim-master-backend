from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({"message": f"Hello, {user.username}!"})

    def post(self, request, *args, **kwargs):
        user = request.user
        return Response({"message": f"Hello, {user.username}!"})
