import smtplib
import os
from google import genai # import文が変わります
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def fetch_korean_words():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    # 【修正ポイント1】 configure ではなく Client を作成する
    client = genai.Client(api_key=api_key)

    prompt = """
    韓国語の日常会話でよく使う単語を10個教えてください。
    以下のフォーマットで出力してください：
    1. [単語] (読み) : [意味]
    """

    # 【修正ポイント2】 client.models.generate_content を使う
    response = client.models.generate_content(
        model='models/gemini-1.5-flash',
        contents=prompt
    )
    
    return response.text

def send_mail():
    # GitHub Secretsから環境変数を読み込む
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    to_email = os.getenv("GMAIL_USER") # 送信先

    # メールの設定
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = "Pythonスクリプトからの自動送信"

    body = fetch_korean_words()
    msg.attach(MIMEText(body, 'plain'))

    try:
        # GmailのSMTPサーバーに接続
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_mail()