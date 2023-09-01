#!/bin/bash

# Install MongoDB and perf analysis tools

sudo apt update
sudo apt upgrade -y

# Common software
sudo apt-get install gnupg curl java-common python2 python3-pip ninja-build cmake gcc g++ zip unzip pkg-config -y

# Install perf
sudo apt-get install linux-tools-generic linux-tools-$(uname -r) -y

# Set default python to python2 for YCSB
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 1

# Install Java
wget https://corretto.aws/downloads/latest/amazon-corretto-17-aarch64-linux-jdk.deb
sudo apt install -y ./amazon-corretto-17-aarch64-linux-jdk.deb

# Instal MongoDB
curl -fsSL https://pgp.mongodb.com/server-6.0.asc |    sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg    --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod

# Instal Maven
wget http://ftp.heanet.ie/mirrors/www.apache.org/dist/maven/maven-3/3.9.4/binaries/apache-maven-3.9.4-bin.tar.gz
sudo tar xzf apache-maven-*-bin.tar.gz -C /usr/local
pushd /usr/local
sudo ln -s apache-maven-* maven
popd
export M2_HOME=/usr/local/maven
export PATH="$M2_HOME/bin:$PATH"

# MongoDB performance test repo
git clone https://github.com/idealo/mongodb-performance-test.git

# Install YCSB
mkdir ycsb && cd ycsb
curl -O --location https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz
tar xfvz ycsb-0.17.0.tar.gz
cd ..

# Telemetry solution for perf
git clone https://git.gitlab.arm.com/telemetry-solution/telemetry-solution.git
pushd telemetry-solution/tools/topdown_tool
sudo pip3 install .
popd

# Streamline gatord (source build)
#git clone https://github.com/ARM-software/gator.git
#pushd gator
#./build-linux.sh
#popd
# Install binary 
[ -f gatord ] && echo "gatord is present" ; chmod +x gatord; sudo cp gatord /usr/local/bin

# Permission for perf
sudo sysctl -w kernel.perf_event_paranoid=-1
