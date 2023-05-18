FROM python:3.9

ENV DEPLOY = 1

WORKDIR /opt/tmp

COPY . /opt/tmp

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y redis-server && apt install -y libgl1-mesa-glx && apt-get install -y libsm6 && apt-get install -y libxrender1 && apt-get install -y libxext-dev

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 80

CMD ["sh", "start.sh"]
