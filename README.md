sociomatrix-reader
==================

Parses a set of survey responses into a sociomatrix.

Dependencies: python 2.7

```
usage: name_importer.py [-h] [--ignoreheaders] [--nicknames NICKNAMES.csv]
                        SURVEY.csv [SURVEY.csv ...]

Process some surveys.

positional arguments:
  SURVEY.csv            a survey to process

optional arguments:
  -h, --help            show this help message and exit
  --ignoreheaders       ignore first row in each CSV file (useful for ignoring
                        column headers)
  --nicknames NICKNAMES.csv
                        a CSV file containing a list of nicknames
```

Takes a list of any number of CSV files. The first column of each CSV file shold contain the names of survey respondents, in the form "LAST, FIRST MIDDLE". The second column of each CSV file should contain a list of names given by each respondent, separated by commas or semicolons. For examples, look at "survey1.csv" and "survey2.csv".

**Output:**

```
[FILENAME_1].matches.csv
[FILENAME_1].sociomatrix.csv
...
[FILENAME_N].matches.csv
[FILENAME_N].sociomatrix.csv
```

Each [FILENAME].matches.csv contains survey responses that were ambiguous, either because there were no matches or multiple matches. This file is meant to be human readable, and should be scanned and corrected by a person (using Excel, for example).

Each [FILENAME].sociomatrix.csv contains a binary matrix which encodes the survey responses. The entry at row I and column J is 1 if respondent I listed respondent J, and 0 otherwise.	NA indicates that the repondent said "no comment".

**Example usage:**
```
$ python name_importer.py survey1.csv survey2.csv --nicknames nicknames.csv
```
==================
License: "MIT license" (free for any purpose as long as license is included).