import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from googletrans import Translator

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
translator = Translator()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.type == 'group':
        if hasattr(event.message, 'mention') and event.message.mention:
            return

    text = event.message.text.strip()

    try:
        detected = translator.detect(text)
        src_lang = detected.lang

        if src_lang.startswith('zh'):
            reply = translator.translate(text, src='zh-TW', dest='th').text
        elif src_lang == 'th':
            reply = translator.translate(text, src='th', dest='zh-TW').text
        elif src_lang == 'en':
            reply = translator.translate(text, src='en', dest='th').text
        else:
            return

    except Exception:
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)