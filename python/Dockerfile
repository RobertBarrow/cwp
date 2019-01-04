FROM python:3
LABEL maintainer="robert.barrow@gmail.com"
ADD --chown=root:root sb.py /usr/local/bin
WORKDIR /data/
ADD --chown=root:root CWP_example.CSV INPUT.CSV
ENTRYPOINT [ "python", "/usr/local/bin/sb.py" ]
CMD [ "/data/INPUT.CSV", "/data/OUTPUT.CSV" ]
