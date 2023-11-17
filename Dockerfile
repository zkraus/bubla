FROM quay.io/centos/centos:stream9
RUN dnf install -y python3.11 python3.11-pip && dnf clean all
RUN python3.11 -m pip --no-cache-dir install poetry
RUN mkdir bubla
WORKDIR /bubla
ADD *.py /bubla
ADD pyproject.toml /bubla
ADD bubla /bubla/bubla
ADD utils /bubla/utils
ADD README.md /bubla
ADD requirements.txt /bubla
RUN poetry install
CMD ["poetry", "run", "python3.11", "main.py"]