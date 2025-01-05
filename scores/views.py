import json
import datetime

from collections import Counter
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from utils.dt import now_tz_offset, humanize_date
from .models import *

SECS_PER_MIN = 60


class ChartParser(object):
    def __init__(self, chart_type, scores):
        self.chart_type = chart_type
        self.scores = scores
        self.data = list()
        self.recent_challenges_threshold = -7

    def generate(self):
        if self.chart_type == "count":
            mode_counts = dict(map(lambda mode: (mode, sum(
                1 for item in self.scores if item['mode'] == mode)), set(item['mode'] for item in self.scores)))
            for mode_count in mode_counts.keys():
                self.data.append({"chart_type": self.chart_type,
                                 "count": mode_counts[mode_count], "indicator": "challenge_game_count" if mode_count == "C" else "chill_game_count"})
            total_seconds = sum(score["game_length"] for score in self.scores)
            average_spm = sum(score["target_hit"]
                              for score in self.scores) / (total_seconds / SECS_PER_MIN)
            self.data.append({"chart_type": self.chart_type,
                             "count": round(average_spm), "indicator": "average_spm"})
            self.data.append({"chart_type": self.chart_type,
                             "count": total_seconds, "indicator": "total_seconds"})

        if self.chart_type == "bar":
            last_challenges = list(filter(lambda s: s["mode"] == "C", self.scores))[
                self.recent_challenges_threshold:]
            self.data.append({"chart_type": "bar", "data": [], "labels": [], "details": []})
            for challenge in last_challenges:
                self.data[0]["data"].append(
                    challenge["target_hit"] * SECS_PER_MIN / challenge["game_length"])
                self.data[0]["labels"].append(humanize_date(challenge["date"]))
                self.data[0]["details"].append("Total Hits: %s, Target Size: %spx, Targets: %s, Game Length: %ssecs" % (
                    challenge["target_hit"], challenge["target_size"], challenge["total_target"], challenge["game_length"]))

        if self.chart_type == "pie":
            self.data.append({"chart_type": "pie", "data": [], "labels": []})
            size_counts = dict(Counter(
                score["target_size"] for score in self.scores).most_common(-self.recent_challenges_threshold))
            for size_count in size_counts.keys():
                self.data[0]["labels"].append("%s PX" % size_count)
                self.data[0]["data"].append(size_counts[size_count])

        if self.chart_type == "polar":
            self.data.append({"chart_type": "polar", "data": [], "labels": []})
            target_counts = dict(Counter(
                score["total_target"] for score in self.scores).most_common(-self.recent_challenges_threshold))
            for target_count in target_counts.keys():
                self.data[0]["labels"].append("%s targets" % target_count)
                self.data[0]["data"].append(target_counts[target_count])

        if self.chart_type == "radar":
            self.data.append({"chart_type": "radar", "data": [], "labels": []})
            challenges = list(filter(lambda s: s["mode"] == "C", self.scores))
            for challenge in challenges:
                challenge["grade"] = round(challenge["target_hit"] * (SECS_PER_MIN / challenge["game_length"]) / (
                    challenge["total_target"] + challenge["target_size"]))
            sorted_challenges = sorted(challenges, key=lambda x: x["grade"], reverse=True)[
                :-self.recent_challenges_threshold]
            for challenge in sorted_challenges:
                self.data[0]["data"].append(challenge["grade"])
                self.data[0]["labels"].append(humanize_date(challenge["date"]))
            # let finalResult = (score * (60 / gameLength)) / (targets + targetSize)
            # export const SCORES = [
            #   {
            #     min: -Infinity,
            #     max: 4,
            #     name: "Awful!",
            #     message: "No disrespect but you suck.",
            #   },
            #   { min: 5, max: 8, name: "D", message: "You are bad." },
            #   { min: 9, max: 12, name: "C", message: "You can do better." },
            #   { min: 13, max: 16, name: "B", message: "You are average." },
            #   { min: 17, max: 20, name: "A", message: "You are above average." },
            #   { min: 21, max: 24, name: "A+", message: "You are elite." },
            #   {
            #     min: 25,
            #     max: Infinity,
            #     name: "Perfect!",
            #     message: "You should consider going pro.",
            #   },
            # ];

        if self.chart_type == "line":
            self.data.append({"chart_type": "line", "datasets": [
                             [], []], "labels": [], "details": []})
            challenges = list(filter(lambda s: s["mode"] == "C", self.scores))[
                self.recent_challenges_threshold:]
            for challenge in challenges:
                challenge["spm"] = challenge["target_hit"] * \
                    (SECS_PER_MIN / challenge["game_length"])
                challenge["grade"] = round(
                    challenge["spm"] / (challenge["total_target"] + challenge["target_size"]))
                self.data[0]["datasets"][0].append(challenge["spm"])
                self.data[0]["datasets"][1].append(challenge["grade"])
                self.data[0]["labels"].append(humanize_date(challenge["date"]))
                self.data[0]["details"].append("Total Hits: %s, Target Size: %spx, Targets: %s, Game Length: %ssecs" % (
                    challenge["target_hit"], challenge["target_size"], challenge["total_target"], challenge["game_length"]))

        return self.data

    def to_json(self):
        return {
            "chart_type": self.chart_type,
            "data": self.data
        }


def process_scores_data(query_set):
    scores = [score["fields"]
              for score in json.loads(serializers.serialize("json", query_set))]
    result = list()
    chart_types = ["count", "bar", "pie", "polar", "radar", "line"]
    for chart_type in chart_types:
        parser = ChartParser(chart_type, scores)
        result.extend(parser.generate())
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
