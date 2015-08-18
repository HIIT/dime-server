FROM ubuntu:15.04
MAINTAINER Mats Sjöberg <mats.sjoberg@helsinki.fi>

# Update OS and install requirements
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install mongodb openjdk-8-jre-headless -y

# Set up environment, copy files
ENV DIME_DIR /srv/dime-server
ENV DIME_JAR ${DIME_DIR}/dime-server.jar
ENV DIME_VERSION 0.1.0

RUN mkdir -p ${DIME_DIR}
ADD build/libs/dime-server-${DIME_VERSION}.jar ${DIME_JAR}

VOLUME ["/var/lib/mongodb"]

# Run on port 8080
EXPOSE 8080
CMD service mongodb start && java -jar ${DIME_JAR}
