FROM python:3

RUN pip install cherrypy

RUN mkdir -p /sbsns/media

EXPOSE 8080:8080

COPY srv /sbsns/srv/
COPY static /sbsns/static/

WORKDIR /sbsns
CMD python srv/srv_main.py
