
# WESP (WORK IN PROGRESS)

This program will automatically monitor a WiFi device for defined parameters using the MAC or IPv4 address. In addition a ping can check if the client is reachable. Will work with Cisco WLC TODO
## Getting Started


### Prerequisites

To clone this repository git is required:

On RHEL / CentOS systems:
```
sudo yum install git
```
On Debian / Ubuntu systems:
```
sudo apt-get install git
```
On Mac:
```
brew install git
```
<br />

If your OS doesn’t ship with Net-SNMP 5.7.x, please follow instructions provided on the [Net-SNMP install page](%28http://www.net-snmp.org/docs/INSTALL.html) to build and install Net-SNMP 5.7.x on your system.

### Installing
Clone repository:
```
git clone https://github.com/IsarNet/wesp
```

Go to folder
```
cd wesp
```

#### Automatic Installation
Run bash script to install dependencies and WESP (root required).
```
sudo bash install_with_dependencies.sh
```

#### Manuel Installation
##### Install dependencies

On Debian / Ubuntu systems:
```
sudo apt-get install libsnmp-dev snmp-mibs-downloader gcc python-dev python-setuptools
```

On RHEL / CentOS systems:
```
sudo yum install net-snmp-devel gcc python-devel python-setuptools
```

On Mac:
```
TODO
```

##### Install WESP

Go to source folder (python installer needs to be run in source folder):
```
cd src
```
Run python installer
```
sudo python setup.py install
```

## Troubleshoot
### Installation
#### Debian  *sudo* not installed:
```
sudo: Command not found
```

Change to root user (enter your password):
```
su
```

Install sudo:
```
apt-get install sudo
```

Allow your user to use sudo (replace *##USERNAME##* with your username):
```
echo "##USERNAME## ALL=(ALL) ALL" >> /etc/sudoers
```

Exit root shell:
```
exit
```

<br>

#### Debian cannot find module *snmp-mibs-installer*:
```
Package 'snmp-mibs-installer' has no installation candidate
```

Add source of package to apt source list:
```
echo "deb http://ftp.br.debian.org/debian/ wheezy main contrib non-free" | sudo tee -a /etc/apt/sources.list
echo "deb-src http://ftp.br.debian.org/debian/ wheezy main contrib non-free" | sudo tee -a /etc/apt/sources.list
```

Update apt:
```
sudo apt-get update
sudo apt-get upgrade
```

## Install Instructions for PyCharm
Can be found [here](https://github.com/IsarNet/wesp/tree/master/doc/PyCharm%20Integeration)


## Authors

* **Marcel Rummens** - *Initial work* - [Rummens](https://github.com/Rummens)
 * **Maximilian Tichter** - *Initial work* - [Maxt2266](https://github.com/maxt2266)


See also the list of [contributors](https://github.com/IsarNet/wesp/contributors) who participated in this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE.txt](LICENSE.txt) file for details

## Acknowledgments

TODO

 [Johannes Luther](https://github.com/netgab).