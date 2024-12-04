FROM python:3.9-slim
WORKDIR /work
COPY app /work/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py"]