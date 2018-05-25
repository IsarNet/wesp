#!/bin/bash

os=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Found OS $os, starting directory : $DIR"

if [[ "$os" == *"Ubuntu"* ]]
then
    echo "Will install for Ubuntu..."
    # install dependencies and check if error happened
    if sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev python-setuptools
    then
        echo "Dependencies installed"
    else
        echo "Error  during installation of Dependencies occurred. Details can be found above"
        exit 1
    fi
    
    #run python installer (installer needs to be run from inside the src folder)
    cd $DIR/src
    echo "Creating man pages..."
    sudo python setup.py --command-packages=click_man.commands man_pages --target /usr/share/man/man1/

    sudo python setup.py install
    echo "Installation completed. Check for errors!"

fi

if [[ "$os" == *"Debian"* ]]
then
    echo "Will install for Debian..."
    # install dependencies and check if error happened
    if sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev python-setuptools
    then
        echo "Dependencies installed"
    else
        echo "Error  during installation of Dependencies occurred. Details can be found above"
        exit 1
    fi


    #run python installer (installer needs to be run from inside the src folder)
    cd $DIR/src
    echo "Creating man pages..."
    sudo python setup.py --command-packages=click_man.commands man_pages --target /usr/share/man/man1/

    sudo python setup.py install
    echo "Installation completed. Check for errors!"

fi

if [[ "$os" == *"CentOS"* ]]
then
    echo "Will install for CentOS..."
    # install dependencies and check if error happened
    if sudo yum install net-snmp-devel gcc python-devel python-setuptools
    then
        echo "Dependencies installed"
    else
        echo "Error  during installation of Dependencies occurred. Details can be found above"
        exit 1
    fi


    #run python installer (installer needs to be run from inside the src folder)
    cd $DIR/src
    sudo python setup.py install

    echo "Creating man pages..."
    sudo python setup.py --command-packages=click_man.commands man_pages --target /usr/share/man/man1/

    echo "Installation completed. Check for errors!"

fi