FROM stuartmarsden/docker-twisted
MAINTAINER nick k ectf@mitre.org

# update sources list
RUN apt-get update && apt-get install -y python-dev \
    python-pip \
    ntpdate
#    texinfo \
#    guile-1.8 \
#    guile-1.8-dev \
#    autoconf \
#    automake \
#    libtool \
#    libgcrypt11-dev \
#    build-essential \
#    autotools-dev \
#    libxml2-dev \
#    check \
#    texinfo \
#    git \
#    html2text \
#    markdown \
#    gawk \
#    pkg-config \
#    wget
#RUN pip install twisted
#RUN git clone https://github.com/cryptotronix/EClet.git
#RUN ./EClet/autogen.sh
#RUN make install

VOLUME /src/pythonlistener/data

COPY server.py /src/pythonlistener/
COPY rsa_key /src/pythonlistener
COPY change_master.py /src/pythonlistener
COPY .yolo /src/pythonlistener/data
COPY registered-widgets.txt /src/pythonlistener/data
COPY requested-widgets.txt /src/pythonlistener/data


EXPOSE 9500

CMD ["python", "/src/pythonlistener/server.py"]
