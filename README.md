sociomatrix-reader
==================

Parses a set of survey responses into a sociomatrix.

REQUIREMENTS:
python

LICENSE:
"MIT license" (free for any purpose as long as license is included).

USAGE:
./name_importer.py [FILENAME].csv

Takes a CSV file where the first column contains the names of survey respondents in the form "LAST, FIRST MIDDLE". The second column contains a list of names given by each respondent, separated by commas or semicolons. For an example, look at "survey.csv".

OUTPUT:
[FILENAME].matches.csv
[FILENAME].sociomatrix.csv
	
[FILENAME].matches.csv contains survey responses that were ambiguous, either because there were no matches or multiple matches. This file is meant to be human readable, and should be scanned and corrected by a person (using Excel, for example).

[FILENAME].sociomatrix.csv contains a binary sociomatrix which encodes the survey responses. The entry at row I and column J is 1 if respondent I listed respondent J, and 0 otherwise.	

