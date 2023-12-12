from openai import OpenAI
import os
import time
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.views import Response
from urllib.error import HTTPError, URLError
# from models import User
# from parameta import Message
load_dotenv()

def create_chat_prompt(parameta):
    # todo: 今後の実装でDBからの情報取得
    prompt_message = f'''
        {parameta}
    '''

    return prompt_message

#主要なプラン生成関数
def chat_with_bot(user_input_kwargs):

    # todo: エラーハンドリングの設定
    gpt_prompt = create_chat_prompt(parameta=user_input_kwargs)

    client = OpenAI(
        api_key=os.environ['OPENAI_API_KEY']
    )

    # todo: ユーザーが公式ラインに初めてアクションをおこした時のみに行う処理
    # user_idを基準にthreadを作成してDBにて使用
    # if user_input_kwargs[0] :
    #     thread = client.beta.threads.create()

    # else:
    #     pass
    thread = client.beta.threads.create()

    try:
        message = client.beta.threads.messages.create(
            thread_id = thread.id,
            role = 'user',
            content = gpt_prompt,
        )

        run = client.beta.threads.runs.create(
            thread_id = thread.id,
            assistant_id = os.environ['OPENAI_API_ASSISTANT_ID'],
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                result_message = client.beta.threads.messages.list(
                    thread_id=thread.id,
                )
                for message in result_message.data:
                    return message.content[0].text.value
            time.sleep(10)
    # hack: もっと他に設定する例外処理があるかもしれない
    except HTTPError as e:
        return Response(e, status=status.HTTP_502_BAD_GATEWAY)