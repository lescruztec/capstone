FROM python:3
COPY .  /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "capstone.asgi:application"]
