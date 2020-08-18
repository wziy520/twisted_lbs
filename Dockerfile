FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 30002
EXPOSE 8000
EXPOSE 80
CMD ["python3", "./twisted/server.py" ]