FROM python:3.10-slim-buster as builder
COPY ./requirements.txt /bot/
WORKDIR /bot
RUN apt-get update && pip3 install -r requirements.txt

FROM python:3.10-slim-buster 
ENV TZ="Asia/Yekaterinburg"
RUN apt-get update && apt-get install --no-install-recommends -y firefox-esr
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./src /bot
WORKDIR /bot/
RUN chmod +x geckodriver  
ENTRYPOINT ["python", "service_bot.py"]