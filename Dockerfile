FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY app/ .
CMD ["streamlit", "run", "app.py", "--server.port=$PORT", "--server.address=0.0.0.0"]
