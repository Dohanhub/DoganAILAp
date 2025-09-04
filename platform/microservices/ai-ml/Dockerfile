FROM python:3.11-slim
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app main.py ./
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

USER app
