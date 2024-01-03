from openai import OpenAI
import os
import time
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.views import Response
from urllib.error import HTTPError, URLError
from line_bot.models import User
from gpt_chat.models import Thread
from django.db import IntegrityError
# from models import User
# from parameta import Message
load_dotenv()

def create_chat_prompt(parameta):
    prompt_message = f'''
        {parameta}
    '''
    return prompt_message


def check_user_and_update_thread(client, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        # userに紐づくthreadを取得
        thread = Thread.objects.filter(user=user).first()

        if thread:
            return thread.thread_id
        else:
            thread = client.beta.threads.create()
            new_thread = Thread.objects.create(thread_id=thread.id, user=user)
            return thread.id
    except User.DoesNotExist:
        try:
            new_user = User.objects.create(user_id=user_id)
            try:
                thread = client.beta.threads.create()
            except HTTPError as e:
                return e
            except URLError as e:
                return e
            new_thread = Thread.objects.create(thread_id=thread.id, user=new_user)
            return thread.id
        except IntegrityError as e:
            return Response('\nIntegrity error is happened in creating user: ' + e)
        except Exception as e:
            return Response('\nError is happend in creating new user: ' + e)
    except Exception as e:
        return Response('\nThis error is happened: ' + e)



def chat_with_bot(user_id, user_input_kwargs):

    gpt_prompt = create_chat_prompt(parameta=user_input_kwargs)

    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY']
    )

    thread_id = check_user_and_update_thread(client, user_id)

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
        return Response('\nHTTP error is happened in creating chat message: '+ e)
    except URLError as e:
        return Response('\nURL error is happened in creating chat message: ' + e)
    except Exception as e:
        return Response('\nThis error is happened in creating chat message: ' + e)
    

def create_single_text_message(user_id, message):
    message = chat_with_bot(user_id, message)
    test_message = [
                {
                    'type': 'text',
                    'text': message
                }
            ]
    return test_message