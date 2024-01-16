import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .chat_with_gpt.conversation import create_single_text_message
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .chat_with_gpt.conversation import chat_with_bot
from .chat_with_gpt.line_message import LineMessage

# Create your views here.
class ChatwitBotView(APIView):
    def post(self, request):
        bot_response = chat_with_bot(request.data["message"])
        return Response(bot_response, status=status.HTTP_200_OK)


# lineに関する機能
@csrf_exempt
def index(request):
    try:
        if request.method == 'POST':
            request = json.loads(request.body.decode('utf-8'))
            print(request)
            data = request['events'][0]
            message = request['events'][0]['message']
            line_user_id = request['events'][0]['source']['userId']
            reply_token = data['replyToken']
            line_message = LineMessage(create_single_text_message(line_user_id, message['text']))
            line_message.reply(reply_token)
            return HttpResponse("ok")
    except ValueError as e:
        return Response({
            "message": "value error in Messaging API",
            "status": e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class ConnectTestResponseView(APIView):
    def get(self, request):
        try:
            return Response("Hello, Django Server", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"something error is happend: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    