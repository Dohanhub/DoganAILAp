FROM python:3.13-slim
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app main.py ./
COPY dashboard_data.py ./
COPY config_manager.py ./
COPY template_engine.py ./
COPY --chown=app:app config/ ./config/
EXPOSE 8501
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8501"]

USER app
