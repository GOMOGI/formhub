FROM ubuntu:14.04

ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

ADD requirements-docker.pip /tmp/requirements-docker.pip
ADD apt-packages.txt /tmp/apt-packages.txt

RUN locale-gen --no-purge en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8

RUN apt-get update -qq
RUN cat /tmp/apt-packages.txt | xargs apt-get --yes --force-yes install

RUN pip install -r /tmp/requirements-docker.pip

ADD ./ /code/

RUN cp /code/docker/files/docker-start.sh /usr/local/bin/startserver.sh
RUN cp /code/docker/files/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
RUN chmod +x /usr/local/bin/startserver.sh

EXPOSE 8000

CMD ["/usr/local/bin/startserver.sh", "-n"]
