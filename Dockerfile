FROM golang:1.20-bullseye

WORKDIR /testing
RUN apt update && apt install -y python3 python3-pip python-is-python3

RUN go install github.com/in-toto/in-toto-golang@latest
RUN pip install in-toto

COPY tests tests

CMD ["python3", "-m", "unittest"]
