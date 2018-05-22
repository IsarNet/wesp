
# WESP (WORK IN PROGRESS)

TODO: One Paragraph of project description goes here

## Getting Started

TODO

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



## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* et