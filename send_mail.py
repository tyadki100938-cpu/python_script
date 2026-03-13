import smtplib
import os
import random
import datetime
from google import genai # import文が変わります
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_study_material():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    # --- バリエーションの設定 ---
    topics = [
        "基礎理論（浮動小数点、キュー・スタック）",
        "コンピュータ構成要素（キャッシュメモリ、パイプライン）",
        "システム構成要素（RAID、稼働率計算）",
        "データベース（第3正規化、SQL）",
        "ネットワーク（OSI参照モデル、TCP/IP、DNS）",
        "セキュリティ（共通鍵・公開鍵、サイバー攻撃手法）",
        "システム開発（アジャイル、テスト手法）",
        "プロジェクトマネジメント（アローダイアグラム、EVM）",
        "サービスマネジメント（ITIL、SLA）",
        "経営戦略・法務（SWOT分析、損益分岐点、著作権）"
    ]
    
    levels = [
        "初級（午前試験の頻出用語）",
        "中級（午前試験の計算・応用）",
        "上級（午後試験を見据えた多角的な解説）"
    ]
    
    styles = [
        "4択クイズ形式",
        "穴埋め形式",
        "記述式（40字以内での説明を求める）",
        "「誤っているものを選べ」というひっかけ形式"
    ]

    # ランダムに組み合わせて「今日のお題」を決定
    topic = random.choice(topics)
    level = random.choice(levels)
    style = random.choice(styles)

    # --- プロンプトの組み立て ---
    prompt = f"""
    あなたは応用情報技術者試験の専門講師です。
    以下の設定で、最高の学習コンテンツを1つ作成してください。
    
    【設定】
    - テーマ: {topic}
    - 難易度: {level}
    - 出題形式: {style}
    
    【構成案】
    1. **解説**: そのテーマで最も重要な点を2つ、実務に即して解説。
    2. **問題**: 設定された形式で1問出題。
    3. **解答と詳細解説**: なぜその答えになるか、他の選択肢がなぜ違うかを論理的に説明。
    """

    # 【重要】 vertexai=False を指定することで、
    # Google AI Studio の API キーモードであることを明示します
    client = genai.Client(
        api_key=api_key,
        vertexai=False 
    )

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
    msg['Subject'] = "応用情報 学習コンテンツ"

    body = generate_study_material()
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
    
    # 結果をファイルに保存（GitHub ActionsでIssueにするため）
    with open("result.md", "w", encoding="utf-8") as f:
        f.write(body)

if __name__ == "__main__":
    send_mail()