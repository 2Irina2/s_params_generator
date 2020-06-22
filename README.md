This is a software application meant to facilitate the design and simulation of passive two-port digital filters through the interpretation of its frequency response from which its scattering parameters will be generated. This project can have a broad applicability in the field of microwave and radio frequency engineering.

Application requires python version 3 to run as well as a few additional GUI and data processing packages. To run the application, run the following command in a python terminal:

`python s_params_generator.py`

The package `texts` contains a text file with the correct and complete input data format that is expected from the application, as well as a file that specifies the list of packages needed to be installed as setup. 

The `configurations.ini` file is a configuration file for several parameters that impact user interaction with tool. For example, displacement step for each point on the each graph at the press of a key, number of lines generated in the touchstone file or graph zoom senzitivity. Application has to be restarted to load new modifications in the configuration file. 

Graph controls: 
* click on point to select it, click on the canvas outside the lines to deselect it
* `A` and `D` keys for navigation among the points on one line
* arrow keys for adjusting the point on the line
* mouse wheel for zooming in and out when point is not selected
* mouse wheel for adjusting point up and down when selected
* `spacebar`to return to initial full view of the graph

The application outputs three files:
* touchstone file for a 2 port device
* text file with manufacturer specifications in the same format expected as input
* text file with adjusted measurements which can be loaded in the input screen
(the last two files are meant to be loaded into the application in case the user needs to pause the development and close the app, allowing them to resume later)
