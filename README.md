
# WESP

This program will automatically monitor a WiFi device for defined parameters using the MAC or IPv4 address. In addition, a ping can check if the client is reachable. 

The project has been developed and tested using a Cisco 2500er series WLC (SW version 8.3.130.0) and Cisco Aironet 802 11n Draft 2.0 Dual Band APs.
## Getting Started


### Prerequisites

To clone this repository git is required:

On RHEL / CentOS systems:
```
sudo yum update; sudo yum install git
```
On Debian / Ubuntu systems:
```
sudo apt-get update; sudo apt-get install git
```
On Mac:
```
brew install git
```
<br />

If your OS doesn’t ship with Net-SNMP 5.7.x, please follow instructions provided on the [Net-SNMP install page](%28http://www.net-snmp.org/docs/INSTALL.html) to build and install Net-SNMP 5.7.x on your system.

**Please note:** To use the database function of this program, install a MySQL instance and make sure the machine 
you’re  using WESP on and the database share the same Timezone. 
<br />
<br />

### Installing
Clone repository:
```
git clone https://github.com/IsarNet/wesp
```

Change folder
```
cd wesp
```

#### Automatic Installation
Run bash script to install dependencies and WESP (root required).
```
sudo bash install_with_dependencies.sh
```
<br />

#### Manual Installation
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
Are already shipped with base OS.
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

<br />
<br />

### Uninstalling

To remove wesp, first get the path to the dependencies:
```
python setup.py install --record files.txt
```

Then remove those files (Note the entries to the modules will remain in the Python path):
```
sudo rm $(cat files.txt)
```

<br />
<br />

## Troubleshoot
### Installation
#### Debian  *sudo* not installed:
```
sudo: Command not found
```
<br />
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

<br />

#### Debian cannot find module *snmp-mibs-installer*:
```
Package 'snmp-mibs-installer' has no installation candidate
```
<br />

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

Rerun bash script.

<br />

#### *Make* command not installed:
```
make: Command not found
```
<br />
On Debian / Ubuntu systems:

```
sudo apt-get install make
```

On RHEL / CentOS systems:

```
sudo yum install make
```

<br />
<br />

## Install Instructions for PyCharm
Can be found [here](https://github.com/IsarNet/wesp/tree/master/doc/PyCharm_Integeration)

<br />
<br />


## WESP Web
A graphical web based user interface can be found [here](https://github.com/IsarNet/wesp_web)

<br />
<br />

## Documentation
The Sphinx doc as html can be found [here](https://github.com/IsarNet/wesp/tree/master/doc/html). To update the documentation run ```make html``` in the base folder of this project.

The Sphinx doc as man file can be found [here](https://github.com/IsarNet/wesp/tree/master/doc/man). To update the documentation run ```make man``` in the base folder of this project.

Activity diagrams can be found [here](https://github.com/IsarNet/wesp/tree/master/doc/Activity_Diagrams).

A class diagram can be found [here](https://github.com/IsarNet/wesp/blob/master/doc/wesp_class_diagram.png).

<br />
<br />

## Authors

* **Marcel Rummens** - *Initial work* - [Rummens](https://github.com/Rummens)
 * **Maximilian Tichter** - *Initial work* - [Maxt2266](https://github.com/maxt2266)


See also the list of [contributors](https://github.com/IsarNet/wesp/contributors) who participated in this project.

<br />
<br />

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE.txt](LICENSE.txt) file for details

<br />
<br />


