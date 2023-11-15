FROM registry.fedoraproject.org/fedora-minimal
RUN microdnf install -y python pip
RUN mkdir bubla
WORKDIR /bubla
ADD *.py /bubla
COPY cogs/ /bubla/cogs
ADD requirements.txt /bubla
RUN pip install -r requirements.txt
CMD ["python", "main.py"]