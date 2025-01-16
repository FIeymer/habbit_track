FROM python:3.10

WORKDIR /server_folder

COPY server_folder/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server_folder/ /server_folder

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
