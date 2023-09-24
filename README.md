# NGUIdleAutoCooking

This simple script is used to manipulate NGUIdle and the Cooking section to automatically
find the best meal efficiency (100%)

## Installation

1. Create a virtual python environment
> py -3 -m venv .venv

2. Activate the python environment
> ./.venv/Scripts/activate

3. Install python project dependencies
> pip install -r requirements.txt

## Running the script

Simply run the CookingSolver.py file from the virtual enviroment.
> ./.venv/Scripts/activate </br>
> python CookingSolver.py

Consideration:

Make sure that the following conditions are met:

- NGUIdle most be opened and the application should be entirely be visible. The script will automatically find it but if any window is above it it may click on that window instead.
- The script takes control of the moust movement and left click. Also, the script cannot be interrupted at the moment. You must wait for the script to be finished before trying to move the mouse again.
