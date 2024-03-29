# Route-Classification
Modules for classifying routes, from FA_sighting files, such as 'SERFR', etc. 

**Overview:**

The purpose of Route Classification is to refine flight paths based on the route that was taken by a flight. This refinement allows for better representation of aircraft noise generated over highly complaining areas. It also makes noise heatmaps clearer and easier to understand for the general audience. The following will explain functions used in the compute-rcas.py, Classify_routes.py, and DataToKeplerMain.py, which are all scripts used in the Route Classification.

**Functions:**



*   compute-rcas.py
    *   Overview:
        *   This function computes the points of closest approach to certain virtual observers/waypoints, using preset conditions for those locations. These conditions include the latitude, longitude, and elevation of those locations. 
    *   In order to input a Sightings file, the compute-rcas.py programs should be run. At the start of this program, a GUI window will prompt the user to select a Sightings file. Then, another GUI window will prompt the user to save the output file name (example is at the top of the GUI window), and choose the folder/location to save it to. 
    *   The points of closest approach are computed by finding the minimum spherical distance between a given flight and a virtual observer/waypoint. After the computation is completed for all of the flights, the minimum spherical distances are output in a .txt file to the location that was chosen by the user.
*   classify_routes.py
    *   read_config	
        *   Overview:
            *   This function reads a configuration file which is externally created. The configuration file has to have the path to the Data Sets by Date folder on the machine. The Data Sets by Date folder should contain both the Sightings file and the FA_rcas files generated by the compute-rcas script. Example of creating a configuration file can be found under the 'Configuration File' section in the Appendix.
            *   An environment variable also needs to be created for this function to work properly. The value for this environment variable needs to be the path to the configuration file made above. The default environment variable is ‘MONA_CFG’. More information on how to create an environment variable can be found under the 'Environment Variable' section in the Appendix.
            *   The purpose of this function is to make the code more robust. It removes all of the hard-coded directories in the script.
    *   Other functions are explained in the script with comments
*   DataToKeplerMain.py
    *   To convert the data from a Sightings file to a file that can be read by [Kepler.gl](https://kepler.gl/), this script utilizes and algorithm which converts the data points given in the Sightings file and visualizes it on the Kepler-compatible file that is created after this program has run. It takes the latitude and longitude from the list that was created by running the classify_routes.py script, and returns a data point that has been visualized and color-coded based on the altitude at that position.









**Appendix:**



*   <span style="text-decoration:underline;">Configuration File:</span>
    *   A configuration file is necessary for the classify_routes script. For creation of this file, open a text editor. The default text editor for Mac users is TextEdit, and the default for Windows users is Notepad. Once a new file has been created, type ‘classify:’ on the first line. On the second line, click tab, and type ‘datafile_basedir:’. In front of this colon, write out the full path of the Data Sets by Date folder (containing the Sightings file and the FA_rcas files created by the compute-rcas script) on your machine. Then, save the file as a .yml. An example configuration file is shown:
    ![](https://github.com/aircraft-noise/Route-Classification/blob/master/docs/images/Config-File1.png)
*   <span style="text-decoration:underline;">Environment Variable:</span>
    *   The environment variable that is used in the classify_routes.py script can be created in at least two of the following ways. If PyCharm is being used for this process, reference the PyCharm section below.
    *   In the shell (Terminal/PowerShell), enter the same directory as the file with the classify_routes code. 
    *   If Terminal is being used (Mac or Linux), type and return `export EnvironmentVariableName = PathToConfigurationFile`
    *   If Windows PowerShell is being used, type and return `setx EnvironmentVariableName “PathToConfigurationFile”`
    *   PyCharm
        *   In order to set the environment variable in PyCharm, first open the Run Configuration selector in the top-right. Then, click on ‘Edit Configurations’ from the drop down menu. This will open the Run/Debug Configurations window. On the left hand side of the menu, there will be a list of scripts. Choose the script with the classify_routes code. Then, on the right, under the ‘Environment’ subsection of the window, click on ‘Environment Variables’. Click the ‘Browse’ icon on the right of the text box, and then click the ‘+’ sign to add a variable. The variable name should be a good representation of the configuration file. The value should be the path towards the configuration file. After the name and value have been entered properly, click ‘Apply’, and exit the window. The environment variable has now successfully been set. Pictures with the steps in order are below.



![](https://github.com/aircraft-noise/Route-Classification/blob/master/docs/images/Route-Classification0.png)




![](https://github.com/aircraft-noise/Route-Classification/blob/master/docs/images/Route-Classification1.png)




![](https://github.com/aircraft-noise/Route-Classification/blob/master/docs/images/Route-Classification2.png)




![](https://github.com/aircraft-noise/Route-Classification/blob/master/docs/images/Route-Classification3.png)



