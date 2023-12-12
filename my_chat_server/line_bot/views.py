from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .chat_with_gpt.conversation import chat_with_bot

# Create your views here.
class ChatwitBotView(APIView):
    # def get(self, request):
    #     return Response("hoge", status=status.HTTP_200_OK)
    
    def post(self, request):
        bot_response = chat_with_bot(request.data["message"])
        return Response(bot_response, status=status.HTTP_200_OK)