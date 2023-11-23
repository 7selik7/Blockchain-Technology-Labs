FROM python:3.10

EXPOSE 5001

WORKDIR /code

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001", "--proxy-headers"]