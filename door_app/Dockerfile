FROM stuartmarsden/docker-twisted
MAINTAINER Embedded CTF ectf@mitre.org

# update sources list
RUN apt-get update

# install pip
RUN apt-get -y install python-pip 

# install python dependancies we need, add more at the end
RUN pip install subprocess

VOLUME /src/pythonlistener/data

COPY server.py /src/pythonlistener/

EXPOSE 9500

CMD ["python", "/src/pythonlistener/server.py"]
