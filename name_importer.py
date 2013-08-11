#!/usr/bin/env python

#Copyright (C) 2013 Daniel J. Butler

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import csv
import re
from difflib import SequenceMatcher
import sys
import copy

def legitchar(c):
	return c == " " or str.isalpha(c)

def longest_common_subseq(a,b):
	s = SequenceMatcher(None, a, b)
	return s.find_longest_match(0, len(a), 0, len(b)).size

def compare_names(written_name,official_name,strictness):
	"""Strictness between 0-4 indicates how confident the match needs to be"""
	written_name = filter(legitchar,written_name).strip()
	if len(written_name.split(' ')) > 1:
		last_written = written_name.split(' ')[-1].upper()
	else:
		last_written = ''
	first_written = written_name.split(' ')[0].upper()
	last_official = official_name.split(', ')[0].split(' ')[-1]
	first_official = official_name.split(', ')[1].split(' ')[0]
	common_len = longest_common_subseq(first_written,first_official)
	if strictness==0:
		# first names match and no last name given
		return first_written==first_official and last_written==""
	if strictness==1:
		# first names overlap by 3 chars and last initials match
		return common_len>=3 and len(last_written)==1 and last_written[0]==last_official[0]
	elif strictness==2:
		# first names match and last initials match
		return first_written==first_official and len(last_written)==1 and last_written[0]==last_official[0]
	elif strictness==3:
		# first names overlap by 3 chars and last names match
		return common_len>=3 and last_written==last_official
	else:
		# first names and last names match
		return first_written==first_official and last_written==last_official

def find_name_in_list(written_name,official_names):
	all_matches = []
	for strictness in reversed(range(5)):
		matches = []
		for i in range(len(official_names)):
			if compare_names(written_name,official_names[i],strictness):
				matches.append(i)
		if len(matches) == 1:
			return matches
        else:
            all_matches += matches
   	return all_matches

def sparse2dense(sparsemat,nrows,ncols):
    # expects a list of lists of indices: [[26], [454], [], [5, 89, 596, 727]]
    dense = []
    for i in range(nrows):
        dense.append([0]*ncols)
        for col in sparsemat[i]:
            dense[i][col] = 1
    return dense
    
def matrix2csv(fname,mat,row_labels,col_labels):
    assert(len(mat)==len(row_labels))
    assert(len(mat[0])==len(col_labels))
    myfile = open(fname, 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow([""]+col_labels)
    for i in range(len(row_labels)):
        wr.writerow([row_labels[i]]+mat[i])
    myfile.close()

HEADERS = [ "Respondee ID", "Respondee name", "What they said",  "Extraneous", "Done - High Confidence", "Done - Inferred from other data", "Too Hard to Call", "Computer generated choices", "What they said - Full list"]

def error_row(resp_id,respondee,written_name,choices,full_resp):
    row = [""] * len(HEADERS)
    row[0] = resp_id
    row[1] = respondee
    row[2] = written_name
    row[7] = choices
    row[8] = full_resp
    return row

def errors2csv(fname,official_names,split_rows,raw_rows,nomatches,multimatches):
    myfile = open(fname, 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(HEADERS)
    for i in range(len(multimatches)):
        for written_name in nomatches[i]:
            wr.writerow(error_row(i,official_names[i],written_name,"",raw_rows[i][1]))
        for (written_name,name_idxs) in multimatches[i]:
            choices = ";  ".join([official_names[name_idx] for name_idx in name_idxs])
            wr.writerow(error_row(i,official_names[i],written_name,choices,raw_rows[i][1]))
    myfile.close()

FNAME = sys.argv[1]
f = open(FNAME,'r')

csv_reader = csv.reader(f)
raw_rows = [];

for row in csv_reader:
    raw_rows.append(row)

f.close()

# Split comma-delimited name-lists
split_rows = copy.deepcopy(raw_rows)
for i in range(len(raw_rows)):
	# split the survey name-lists on commas or semicolons
	split_rows[i][1] = [s.strip() for s in re.split(';|,',raw_rows[i][1])]

# Remove "none"-like reponses that indicate an empty list
empty_terms = ['','None','none']
for i in range(len(split_rows)):
#TODO: "" should probably be treated differently since it may indicate no reponse at all
	split_rows[i][1] = [s for s in split_rows[i][1] if s not in empty_terms]

# Column 0 gives the names of the survey respondents
official_names = [row[0] for row in split_rows]

# Names in survey responses that were successfully matched to a UNIQUE respondent name
matches = range(len(split_rows))
# Names in survey responses that were not matched to ANY respondent name
nomatches = range(len(split_rows))
# Names in survey responses that were matched to MULTIPLE respondent name
multimatches = range(len(split_rows))

# Main loop
for i in range(len(split_rows)):
    print("Processing row %d" % i)
    matches[i] = []
    nomatches[i] = []
    multimatches[i] = []
    for written_name in split_rows[i][1]:
        name_idxs = find_name_in_list(written_name,official_names)
        if len(name_idxs) == 1:
            matches[i] += name_idxs
        elif len(name_idxs) == 0:
            nomatches[i].append(written_name)
        elif len(name_idxs) > 1:
            multimatches[i].append((written_name,name_idxs))

# Save the match matrix
match_mat = sparse2dense(matches,len(official_names),len(official_names))
basename = sys.argv[1].split('.')[0]
matrix2csv(basename + ".sociomatrix.csv",match_mat,official_names,official_names)
errors2csv(basename + ".matches.csv",official_names,split_rows,raw_rows,nomatches,multimatches)

# save the nomatches
# print_errors(basename + ".failures.txt",multimatches,nomatches)
