#!/bin/bash

os=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $os
echo $DIR

if [[ "$os" == *"Ubuntu"* ]]
then
    echo "Will install for Ubuntu..."
    # install dependencies and check if error happened
    if sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev git python-setuptools
    then
        echo "Dependencies installed"
    else
        echo "Error  during installation of Dependencies occurred"
        exit 1
    fi
    
    #run python installer (installer needs to be run from inside the src folder)
    cd $DIR/src
    sudo python setup.py install
    echo "Installation completed. Check for errors!"

fi

if [[ "$os" == *"Debian"* ]]
then
    echo "Will install for Debian..."
    # install dependencies and check if error happened
    if sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev git python-setuptools
    then
        echo "Dependencies installed"
    else
        echo "Error  during installation of Dependencies occurred"
        exit 1
    fi


    #run python installer (installer needs to be run from inside the src folder)
    cd $DIR/src
    sudo python setup.py install
    echo "Installation completed. Check for errors!"

fi