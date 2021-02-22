FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# TODO: порты
# TODO: 0.0.0.0

CMD [ "python3", "./hello.py" ]