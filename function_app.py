import azure.functions as func
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_dream_interpretation(user_message):
    print("get_dream_interpretation")
    message_format = f"""{user_message}以下のフォーマットに従い、{user_message}に関する夢占いの結果を回答してください。
具体性とポジティブなトーンを心掛け、独自のデータを基にして断定的な解釈を提供してください。また、ユーザーが前向きな気持ちになるようなアドバイスを含めること。¥n ¥n
#夢占いの出力フォーマット¥n ¥n 🔮夢占いの結果🔮¥n [夢の内容に合わせた適切な絵文字]あなたの夢: [夢の内容]　🔍¥n ¥n
🌟夢の意味:¥n
- [夢の要素1]: [独自データに基づいた解釈] [適切な絵文字]¥n
- [夢の要素2]: [独自データに基づいた解釈] [適切な絵文字]¥n
🔑解釈:¥n"
- あなたは[夢の要素や状況]において、[断定的な見解]を持っています。[状況が示唆する心理状態や能力に関する断定的な解釈]。¥n¥n
🚀メッセージ:¥n"
- この夢は、[夢の内容が示唆する行動や変化]のためのサインです。[ポジティブな行動や心構えに関するアドバイス]。[未来に向けたポジティブなメッセージ]。✨"""
    chat_completion = openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message_format,
                }
            ],
            model="gpt-4",
        )
    return chat_completion.choices[0].message.content


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("handle_message")
    line_user_id = event.source.user_id
    # todo
    user_message = event.message.text
    print(user_message)
    resp_message = get_dream_interpretation(user_message)
    line_bot_api.push_message(
        line_user_id,
        TextSendMessage(text=resp_message)
    )


@app.route(route="get_line_bot", auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def get_line_bot(req: func.HttpRequest) -> func.HttpResponse:
    print("get_line_bot")
    signature = req.headers['X-Line-Signature']
    body = req.get_body().decode("utf-8")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return func.HttpResponse(status_code=400)
    return func.HttpResponse(
        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        status_code=200
    )


@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

