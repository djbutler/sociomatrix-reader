sociomatrix-reader
==================

Parses a set of survey responses into a sociomatrix.

Dependencies: python 2.7

Usage:

$ python name_importer.py [FILENAME_1].csv [FILENAME_2].csv ... [FILENAME_N].csv

Takes a list of any number of CSV files. The first column of each CSV file shold contain the names of survey respondents, in the form "LAST, FIRST MIDDLE". The second column of each CSV file should contain a list of names given by each respondent, separated by commas or semicolons. For examples, look at "survey1.csv" and "survey2.csv".

Output:

[FILENAME_1].matches.csv
[FILENAME_1].sociomatrix.csv
...
[FILENAME_N].matches.csv
[FILENAME_N].sociomatrix.csv

Each [FILENAME].matches.csv contains survey responses that were ambiguous, either because there were no matches or multiple matches. This file is meant to be human readable, and should be scanned and corrected by a person (using Excel, for example).

Each [FILENAME].sociomatrix.csv contains a binary matrix which encodes the survey responses. The entry at row I and column J is 1 if respondent I listed respondent J, and 0 otherwise.	NA indicates that the repondent said "no comment".

Example:
python name_importer.py survey1.csv survey2.csv

==================
License: "MIT license" (free for any purpose as long as license is included).