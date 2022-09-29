FROM python:latest

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . /api

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--proxy-headers", "--port", "1234"]"

