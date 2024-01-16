from openai import OpenAI
import os
import time
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.views import Response
from urllib.error import HTTPError, URLError
from line_bot.models import User
from gpt_chat.models import Thread
load_dotenv()

def create_chat_prompt(parameta):
    prompt_message = f'''
        {parameta}
    '''
    return prompt_message


def check_user_and_update_thread(client, line_user_id):
    try:
        user = User.objects.get(user_id=line_user_id)
        # userに紐づくthreadを取得
        thread = Thread.objects.filter(user=user).first()

        if thread:
            return thread.thread_id
        else:
            thread = client.beta.threads.create()
            Thread.objects.create(thread_id=thread.id, user=user)
            return thread.id
    except User.DoesNotExist:
        try:
            new_user = User.objects.create(user_id=line_user_id)
            thread = client.beta.threads.create()
            Thread.objects.create(thread_id=thread.id, user=new_user)
            return thread.id
        except HTTPError as e:
            return Response({
                "messsage":"An URL error occurs in using openai API ",
                "status": e,
                }, status=status.HTTP_400_BAD_REQUEST)
        except URLError as e:
            return Response({
                "messsage":"An URL error occurs in using openai API ",
                "status": e,
                }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "messsage":"An error occurs in creating user",
            "status": e,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def chat_with_bot(line_user_id, user_input_kwargs):

    gpt_prompt = create_chat_prompt(parameta=user_input_kwargs)

    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY']
    )

    thread_id = check_user_and_update_thread(client, line_user_id)

    try:
        message = client.beta.threads.messages.create(
            thread_id = thread_id,
            role = 'user',
            content = gpt_prompt,
        )

        run = client.beta.threads.runs.create(
            thread_id = thread_id,
            assistant_id = os.environ['OPENAI_API_ASSISTANT_ID'],
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                result_message = client.beta.threads.messages.list(
                    thread_id=thread_id,
                )
                for message in result_message.data:
                    return message.content[0].text.value
            time.sleep(1)
    except HTTPError as e:
        return Response({
            "messsage":"An URL error occurs in using openai API ",
            "status": e,
            }, status=status.HTTP_400_BAD_REQUEST)
    except URLError as e:
        return Response({
            "messsage":"An URL error occurs in using openai API ",
            "status": e,
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "messsage":"An error occurs in using openai API",
            "status": e,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

def create_single_text_message(user_id, message):
    message = chat_with_bot(user_id, message)
    test_message = [
                {
                    'type': 'text',
                    'text': message
                }
            ]
    return test_message