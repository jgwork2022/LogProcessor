FROM python:3.7

WORKDIR /src

COPY ./src/ .

ENTRYPOINT [ "python", "-m" , "main"]