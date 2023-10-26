# NGUIdleAutoCooking

This simple script is used to manipulate NGU Idle and the Cooking section to automatically
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

### Considerations

Please read the following notes:

- NGU Idle must be opened and the application should be entirely be visible. The script will automatically find it but if any window is above it it may click on that window instead.
- The script takes control of the moust movement and left click. Also, the script cannot be interrupted at the moment. You must wait for the script to be finished before trying to move the mouse again.
- The script will try to automatically detect the number of ingredients available (6, 7 or 8), altough it was only tested with 6 ingredients.

### Output example

```
INFO:root:nb ingredients: 6
Reset ingredients to 0
Iterate one ingredient at a time while the rest is set to 0
Find duplicated ingredients
pairs and singles: [array([0, 4]), array([1]), array([2, 3]), array([5])]
Find all peaks
Identify all best values for each pair
Found ingredients ing 0 : 19, ing 4 : 19 with %36.98 efficiency
Found ingredients ing 2 : 2, ing 3 : 5 with %84.01 efficiency
Identify all best values for unmatched ingredients
Found ingredient ing 1 : 6 with %94.24 efficiency
Found ingredient ing 5 : 2 with %100.0 efficiency
Found the perfect solution!
```
