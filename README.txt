Welcome to PyMOL360!

For optimal PyMOL360 experience, we recommend using PyMol v1.3
	Example: Windows users download pymol-v1.3r1-edu-Win32.msi

Before running this add-on in PyMOL, you will need to add the Pygame module to your PyMOL library. To do this, follow these steps:

1. Obtain a copy of Pygame that is compatible with the your version of PyMOL.
	This package includes the version of Pygame that is necessary for running with PyMOL v1.3, Python 2.5.
	Alternatively, visit the main PyGame download page: http://www.pygame.org/download.shtml, then identify the appropriate .msi installation package for your system.

2. After obtaining the Pygame files, place the Pygame folder directly into "...\PyMOL\py25\Lib\site-packages" within the home directory for your PyMOL program
	Standard location for Windows: 
		"C:\Program Files (x86)\PyMOL\PyMOL\py25\Lib\site-packages" or
		"C:\Program Files\PyMOL\PyMOL\py25\Lib\site-packages"

	You now have the PyGame module on your PyMOL instance!

Now you have the module, to run the program you just need to execute the script. Either:

A) Move the script, PyMOL360.py, to the PyMOL instance working directory 
	To determine the PyMOL home directory, open PyMOL and enter the command "pwd" (print working directory)
	Windows users will typically have the directory "...Username/Documents"
B) Navigate to the directory containing the script using "cd <path to folder>"

Finally, begin exploring molecular structures with the comfort of your favorite gaming controller!
	Within PyMOL, enter the command "run PyMOL360.py", followed by "PyMOL360"

A full walkthrough of PyMOL360 can be found in an additional document found at: https://github.com/HackelLab-UMN/PyMOL360
	
Note: Altering the main viewing window while running PyMOL360 may result in an error. To avoid this, set window to full screen, then run script.

If you have comments or questions, please contact:

Benjamin Hackel
hackel@umn.edu
University of Minnesota