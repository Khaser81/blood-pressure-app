FROM python:3.11-slim

WORKDIR /app

# 依存関係をインストール
COPY app/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# アプリをコピー
COPY app/ .

# StreamlitをRender用ポートで起動
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
