
FROM python:3.8
 
EXPOSE 5432
 
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install gdal-bin gettext libgettextpo-dev -y
 
COPY requirements.txt /requirements.txt
 
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
 
COPY ./LAMA_ucup ./app
 
COPY ./docker/app/start.sh /start
RUN chmod +x /start
RUN sed -i 's/\r//' /start
RUN chmod 755 /start
 
WORKDIR /app

# FROM python:3.8

# COPY requirements.txt /requirements.txt
# RUN pip3 install --upgrade pip
# RUN pip3 install -r /requirements.txt

# COPY . ./app

# EXPOSE 8001

# WORKDIR /app