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
	
==================

Copyright (C) 2013 Daniel J. Butler

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.