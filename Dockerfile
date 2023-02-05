FROM python:3.10.0-alpine3.13 as builder
RUN apk update \
    && apk upgrade \
    && apk add --no-cache bash \
    libffi-dev \
    gcc \
    musl-dev
COPY ./src/requirements.txt /bot/
WORKDIR /bot/
RUN cd /bot/ && pip3 install -r requirements.txt 


From python:3.10.0-alpine3.13
ENV TZ="Asia/Yekaterinburg"
RUN apk update \
    && apk upgrade \
    && apk add --no-cache firefox 
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./src /bot
WORKDIR /bot/
RUN chmod +x geckodriver  
ENTRYPOINT ["python", "service_bot.py"]
