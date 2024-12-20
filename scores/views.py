import json
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from utils.dt import now_tz_offset
from .models import *


def process_scores_data(query_set):
    scores = json.loads(serializers.serialize("json", query_set))
    result = list()
    for score in scores:
        result.append(score["fields"])
    return result


class ScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        scores = Score.objects.filter(user=user)
        if scores:
            return Response({"data": process_scores_data(scores)}, status=status.HTTP_200_OK)
        return Response({"message": f"Hello, {user.username}!"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            date = now_tz_offset(request.data.get("tz_offset"))
            entity = Score(user=user, date=date, game_length=request.data.get("game_length"), target_size=request.data.get(
                "target_size"), total_target=request.data.get("total_target"), target_hit=request.data.get("target_hit"), mode=request.data.get("mode"))
            entity.save()
            print(user.username, request.data)
            return Response({"message": f"Hello, {user.username}!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error when saving score, %s" % e)

        return Response(status=status.HTTP_400_BAD_REQUEST)
