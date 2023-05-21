FROM python:3.9

ENV DEPLOY = 1

WORKDIR /opt/tmp

COPY . /opt/tmp

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y redis-server

RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 80

CMD ["sh", "start.sh"]
