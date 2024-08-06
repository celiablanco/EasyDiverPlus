#/bin/bash

sudo apt update
sudo apt-get install -y zlib1g-dev libbz2-dev libltdl-dev libtool zlib1g-dev pkg-config autoconf make python3 python3-pip
git clone http://github.com/neufeld/pandaseq.git/
cd ./pandaseq
bash ./autogen.sh && MAKE=gmake ./configure && make && sudo make install

which pandaseq
