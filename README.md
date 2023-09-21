# FlashLogger
PyJEM script to log the gun conditions following a flash of the cold FEG gun and log values to a csv file.

Intended for a JEOL F200 STEM with a cFEG.

## Simple UI:

TEM user inputs name, checks the boxes if the conditions have been met, the type of flash (low or high) and any notes to be taken at the same time (eg any errors or user notes). It will even tell the user what type of flash needs to be done. 

There are 2 versions depending on the ui you have installed. the pyqt5 version is not being developed any further at the moment.

## Usage
Open the program. It is important to only click the log button **after** the emission has been turned on,
Data log is saved to C:\Data\FLasher\log.csv

TODO: get vacuum values

