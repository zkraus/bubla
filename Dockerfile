FROM quay.io/centos/centos:stream9
RUN dnf install -y python3.11 python3.11-pip && dnf clean all
RUN mkdir bubla
WORKDIR /bubla
ADD *.py /bubla
COPY cogs/ /bubla/cogs
ADD requirements.txt /bubla
RUN python3.11 -m pip install -r requirements.txt
CMD ["python3.11", "main.py"]