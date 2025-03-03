#!/bin/bash

# Author: Manohar Barma
# Description: Terraform installation script
# Version: 1.0
# Date: 03-03-2025
# Contact: manoharbarma07@gmail.com

# Updating package lists
echo "Updating package lists..."
sudo apt update -y

# Add HashiCorp GPG key
echo "Adding HashiCorp GPG key..."
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# Add HashiCorp repository
echo "Adding HashiCorp repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

# Updating package lists again after adding the new repository
echo "Updating package lists after adding HashiCorp repository..."
sudo apt update -y

# Install Terraform
echo "Installing Terraform..."
sudo apt install -y terraform

# Verify installation
echo "Terraform installation complete!"
terraform version
