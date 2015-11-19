FROM ubuntu:14.04

ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

ADD ./ /code/

RUN locale-gen --no-purge en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8

RUN apt-get update -qq
RUN cat /code/apt-packages.txt | xargs apt-get --yes --force-yes install

EXPOSE 8000 8983

CMD ["echo", "hello world"]
