#!/bin/bash

os=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $os
echo $DIR

if [[ "$os" == *"Ubuntu"* ]]
then
    echo "Will install for Ubuntu..."
    # install dependencies
    sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev git python-setuptools
    echo "Dependencies installed"
    
    #run python installer
    sudo python $DIR/setup.py install
    echo "Installation completed. Check for errors!"

fi

if [[ "$os" == *"Debian"* ]]
then
    echo "Will install for Debian..."
    # install dependencies
    sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev git python-setuptools
    echo "Dependencies installed"

    #run python installer
    sudo python $DIR/setup.py install
    echo "Installation completed. Check for errors!"

fi