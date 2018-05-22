#!/bin/bash

os=$(awk -F= '/^NAME/{print $2}' /etc/os-release)

echo $os

if [[ "$os" == '"Ubuntu"' ]]
then
    echo "Will install for Ubuntu..."
    # install dependencies
    sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev git python-setuptools
    echo "Dependencies installed"
    
    #run python installer
    sudo src/python setup.py install
    echo "Installed wesp successfully"

fi