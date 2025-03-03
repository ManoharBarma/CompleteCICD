#!/bin/bash

# Author: Manohar Barma
# Description: Kubernetes kubectl installation script
# Version: 1.0
# Date: 03-03-2025
# Contact: manoharbarma07@gmail.com

# Set the latest stable version
KUBECTL_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)

# Download kubectl binary
echo "Downloading kubectl version: $KUBECTL_VERSION"
curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"

# Download SHA256 checksum
curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256"

# Verify the binary
echo "Verifying checksum..."
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

# Install kubectl
echo "Installing kubectl..."
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client

echo "kubectl installation complete!"
