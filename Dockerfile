# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係をインストール
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Streamlitも直接指定（requirementsに含まれないFastAPI環境用補完）
RUN pip install --no-cache-dir streamlit pandas matplotlib plotly

# プロジェクト全体をコピー
COPY . .

# Renderの環境変数PORTを使ってStreamlitを起動
CMD streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
