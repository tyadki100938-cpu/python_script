import smtplib
import os
import random
import datetime
from google import genai # import文が変わります
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def fetch_korean_words():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    # 【重要】 vertexai=False を指定することで、
    # Google AI Studio の API キーモードであることを明示します
    client = genai.Client(
        api_key=api_key,
        vertexai=False 
    )

    # 1. 10個のパーソナライズされたトピック
    topics = [
        "韓国の最新トレンド・SNS新造語",
        "カフェ巡りやグルメ、食レポで使える表現",
        "韓国ドラマの感情豊かなセリフ・恋愛表現",
        "ビジネスメール・オフィスでの敬語",
        "IT・テクノロジー・ガジェットに関する用語",
        "旅行中のトラブル解決・現地の人との交流",
        "性格や感情を細かく表す副詞・形容詞",
        "ファッション・美容・コスメに関する専門用語",
        "料理のレシピや味の表現（食感など）",
        "K-POPの歌詞によく出る詩的な表現"
    ]
    
    # 2. 実行ごとにランダムに選択
    selected_topic = random.choice(topics)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 3. 動的なプロンプトの組み立て
    prompt = f"""
    あなたはパーソナライズされた韓国語講師です。
    実行時刻: {current_time}
    
    今回の重点テーマ: 【{selected_topic}】
    
    上記テーマに沿った、中〜上級レベルの韓国語単語を「10個」教えてください。
    
    【出力ルール】
    1. 超基本単語（안녕하세요, 감사합니다 等）は絶対に含めない。
    2. 以下のフォーマットで出力すること：
       - 単語(ハングル) / 読み(カタカナ) / 意味
       - その単語を使った実用的な例文（日本語訳付き）
    3. 10個のうち2個は、そのテーマに関連する「最新の流行語」や「慣用句」を混ぜてください。
    4. 重複を避けるため、独自の選定アルゴリズムを用いて、前回の出力とは異なる語彙を選んでください。
    """
    
    # model名はそのままで大丈夫です
    response = client.models.generate_content(
        model="models/gemini-2.5-flash", 
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