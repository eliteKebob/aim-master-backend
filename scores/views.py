from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.dt import now_tz_offset
from .models import *

class ScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({"message": f"Hello, {user.username}!"})

    def post(self, request, *args, **kwargs):
        user = request.user
        date = now_tz_offset(request.data.get("tz_offset"))
        entity = Score(user=user, date=date, game_length=request.data.get("game_length"), target_size=request.data.get("target_size"), total_target=request.data.get("total_target"), target_hit=request.data.get("target_hit"), mode=request.data.get("mode"))
        entity.save()
        print(user.username, request.data)
        return Response({"message": f"Hello, {user.username}!"})
