FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py ./
COPY dashboard_data.py ./
COPY config_manager.py ./
COPY template_engine.py ./
COPY config/ ./config/
EXPOSE 8501
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8501", "--reload", "--reload-dir", "/app"]
