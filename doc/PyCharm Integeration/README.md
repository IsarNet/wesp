  
## Install Instructions for PyCharm  
  
  
1. [Download](https://www.jetbrains.com/pycharm/download/#section=mac) latest version of GitHub (Community or Professional):   
<br>
2. Enter you GitHub credentials in Preferences -> Version Control -> GitHub. More details can be found [here](https://www.jetbrains.com/help/pycharm/settings-version-control-github.html). 
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/github%20.png?raw=true)
<br><br>
3. Make a checkout of the repository: VCS -> Checkout from Version Control -> Git 
![VCS Checkout](vcs_check_out.png)
<br><br>
4. Clone the repository (https://github.com/IsarNet/wesp/) to your computer. 
![Clone Repository](clone_repository.png)
<br><br>
5. Confirm the Checkout: 
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/Checkout_confirm.png?raw=true)
<br><br>
6. Open the created project and go to Settings -> Project: wesp -> Project Interpreter. Here create a new local python interpreter, by clicking on the settings icon in the top right corner and selecting *Add Local...*
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/set_project_intrepeter.png?raw=true)
<br> <br>
8. Create a new python 2.7 interpreter or use the one from your OS. Hit *OK* to confirm. ![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/virtual_env.png?raw=true)
<br><br>
9. Hit Apply.
<br> <br>
10. Select *Project Structure* from the right menu. Click on the *src* folder and mark it as *Sources* using the button on the top. Select the *venv* folder and mark it as *Excluded*.  Confirm everything by clicking on *OK*.
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/project_structure.png?raw=true)
<br><br>
11. Find the file *requirements.txt* from the Project Structure on the left and open it. Install the requirements using the yellow bar on the top (it may take a few seconds to appear). If something cannot be installed, make sure you use the newest version of PyCharm. 
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/install_requirements.png?raw=true)
<br><br>
12. Find the file *\__init__.py* in the module *wesp* of the folder *src*. Right click and select *Run '\__init__'.* 
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/run_init.png?raw=true)
<br><br>
13. The console should appear and print something like this: 
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/try_run_results.png?raw=true)
<br><br>
14. You can now starting to develop. To add parameter to the execution change the Run Configuration: Run -> Edit Configurations. 
![enter image description here](https://github.com/IsarNet/wesp/blob/master/doc/PyCharm%20Integeration/config_parameter.png?raw=true)
<br><br>
16. Changes can directly be committed and pushed to GitHub. More information can be found [here](https://www.jetbrains.com/help/pycharm/commit-and-push-changes.html).