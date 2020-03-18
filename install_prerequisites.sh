#!/bin/bash

# Install Docker as described in https://docs.docker.com/install/linux/docker-ce/ubuntu/
# Prepare environment
sudo apt-get remove docker docker-engine docker.io
sudo apt-get update

# Add further dependencies
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

# Add Docker package repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Install Docker and add user
sudo apt-get update
sudo apt-get install -y docker-ce 
sudo groupadd docker
sudo usermod -aG docker ${USER}
docker run hello-world