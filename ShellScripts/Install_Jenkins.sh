#!/bin/bash

# Author: Manohar Barma
# Description: Jenkins installation and configuration script
# Version: 1.0
# Date: 24-02-2025
# Contact: manoharbarma07@gmail.com


# Updating package lists
sudo apt update -y

# Installing JDK 17
sudo apt install -y fontconfig openjdk-17-jre
java -version

# Adding Jenkins repository key and source
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian/jenkins.io-2023.key
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

# Installing Jenkins
sudo apt update -y
sudo apt install -y jenkins

# Changing port from 8080 to 8081
sudo sed -i 's/Environment="JENKINS_PORT=8080"/Environment="JENKINS_PORT=8081"/' /lib/systemd/system/jenkins.service
sudo systemctl daemon-reload
sudo systemctl restart jenkins

echo "Jenkins installation complete. Access it at: http://localhost:8081"


