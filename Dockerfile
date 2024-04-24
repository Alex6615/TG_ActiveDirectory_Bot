# Base image
FROM python:3.9.16-alpine

# Install dependencies
RUN apk upgrade
RUN apk --update \
    add gcc \
    make \
    build-base \
    g++
#    add chromium-chromedriver  \
#    openjdk11 \
#    git \
#    curl \
#    bash \
#    sqlite
    
# RUN rm /var/cache/apk/*

COPY . /ADUser_unlock
WORKDIR /ADUser_unlock
RUN pip3 install -r requirements.txt
RUN python3 /ADUser_unlock/bak/setup.py build_ext --inplace
RUN rm -rf /ADUser_unlock/bak
RUN rm -rf /ADUser_unlock/build
RUN rm -r ~/.cache/pip    

# Listen port
# EXPOSE 9453

# Run the application
ENTRYPOINT ["python3", "app.py"]

