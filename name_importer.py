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
import argparse

def legitchar(c):
    return c == " " or c == "," or str.isalpha(c)


def longest_common_subseq(a, b):
    s = SequenceMatcher(None, a, b)
    return s.find_longest_match(0, len(a), 0, len(b)).size
    

def psuedo_edit_distance(s1, s2):
    a = b = size = distance = 0
    for m in SequenceMatcher(a=s1, b=s2).get_matching_blocks():
        distance += max(m.a-a, m.b-b) - size
        a, b, size = m
    return distance

def psuedo_edit_ratio(s1, s2):
    a = b = size = distance = 0
    return SequenceMatcher(a=s1, b=s2).ratio()
    
    
def compare_names(written_name, official_name, nicknames, strictness):
    """Strictness between 0-4 indicates how confident the match needs to be"""
    # important cases:
    #   First Last
    #   First Middle Last
    #   Middle Last
    #   Middle L.
    #   Middle L
    #   First L.
    #   First L
    #   Last, First
    ###
    # pre-process written_name
    written_name = filter(legitchar, written_name).strip()
    if ',' in written_name:
        first_written = written_name.split(',')[-1].strip().split(" ")[0].upper()
        last_written = written_name.split(',')[0].strip().upper()
    else:
        if len(written_name.split(' ')) > 1:
            last_written = written_name.split(' ')[-1].upper()
        else:
            last_written = ''
        first_written = written_name.split(' ')[0].upper()
    # pre-process official_name
    if ',' in official_name:
        last_official = official_name.split(', ')[0].split(' ')[-1]
        first_official = official_name.split(', ')[1].split(' ')[0]
        middle_official = official_name.split(', ')[1].split(' ')[-1]
    else:
        last_official = official_name.split(' ')[-1]
        first_official = official_name.split(' ')[0]
        middle_official = official_name.split(' ')[-1]
    common_len = longest_common_subseq(first_written, first_official)
    first_match = first_written == first_official or first_written in nicknames
    last_match = last_written == last_official or (len(last_written) >= 5 and len(last_official) >= 5 and psuedo_edit_ratio(last_written, last_official) >= 0.8)
    if strictness == 0:
        # first names match and no last name given
        return first_match and last_written == ""
    if strictness == 1:
        # first names overlap by 3 chars and last initials match
        return common_len >= 3 and len(last_written) == 1 and last_written[0] == last_official[0]
    elif strictness == 2:
        # first names match and last initials match
        return first_match and len(last_written) == 1 and last_written[0] == last_official[0]
    elif strictness == 3:
        # first names overlap by 3 chars and last names match
        return common_len >= 3 and last_match
    elif strictness == 4:
        # first initials match and last names match
        return len(first_written) > 0 and first_written[0] == first_official[0] and last_match
    elif strictness == 5:
        # written first matches official middle and last names match
        return first_written == middle_official and last_match
    else:
        # first names and last names match
        return first_match and last_match


def find_name_in_list(written_name, official_names, nicknames):
    all_matches = []
    for strictness in reversed(range(7)):
        matches = []
        for i in range(len(official_names)):
            if compare_names(written_name, official_names[i], nicknames.get(official_names[i], []), strictness):
                matches.append(i)
        if len(matches) == 1:
            return matches
        else:
            all_matches += matches
    return all_matches

def matrix2csv(fname, mat, row_labels, col_labels):
    assert (len(mat) == len(row_labels))
    assert (len(mat[0]) == len(col_labels))
    myfile = open(fname, 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow([""] + col_labels)
    for i in range(len(row_labels)):
        wr.writerow([row_labels[i]] + mat[i])
    myfile.close()


HEADERS = ["Respondee ID", "Respondee name", "What they said", "Extraneous", "Done - High Confidence",
           "Done - Inferred from other data", "Too Hard to Call", "Computer generated choices",
           "What they said - Full list"]


def error_row(resp_id, respondee, written_name, choices, full_resp):
    row = [""] * len(HEADERS)
    row[0] = resp_id
    row[1] = respondee
    row[2] = written_name
    row[7] = choices
    row[8] = full_resp
    return row


def errors2csv(fname, official_names, row_labels, raw_rows, nomatches, multimatches):
    myfile = open(fname, 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(HEADERS)
    for i in range(len(multimatches)):
        for written_name in nomatches[i]:
            wr.writerow(error_row(i, row_labels[i], written_name, "", raw_rows[i][1]))
        for (written_name, name_idxs) in multimatches[i]:
            choices = ";  ".join([official_names[name_idx] for name_idx in name_idxs])
            wr.writerow(error_row(i, row_labels[i], written_name, choices, raw_rows[i][1]))
    myfile.close()
    
def read_csv(fname, ignoreheaders=False):
    f = open(fname, 'r')

    csv_reader = csv.reader(f)
    raw_rows = [row for row in csv.reader(f.read().splitlines())]
    
    for row in csv_reader:
        raw_rows.append(row)

    f.close()
    
    if ignoreheaders:
        raw_rows = raw_rows[1:]
    return raw_rows

parser = argparse.ArgumentParser(description='Process some surveys.')
parser.add_argument('surveys', metavar='SURVEY.csv', nargs='+',
                   help='a survey to process')
parser.add_argument('--ignoreheaders', action='store_true',
                   help='ignore first row in each CSV file (useful for ignoring column headers)')
parser.add_argument('--nicknames', metavar='NICKNAMES.csv',
                   help='a CSV file containing a list of nicknames')

args = parser.parse_args()
print args

FNAMES = args.surveys

# load nicknames, if present
nicknames = {}
if args.nicknames:
    nickname_rows = read_csv(args.nicknames, ignoreheaders=args.ignoreheaders)
    nicknames = dict([(r[0].strip(), [s.strip().upper() for s in r[1].strip().split(',')]) for r in nickname_rows])
    from pprint import pprint
    pprint(nicknames)

# get official_names list (union of the names in all the files)
official_names = []
for fname in FNAMES:
    raw_rows = read_csv(fname, ignoreheaders=args.ignoreheaders)

    # Column 0 gives the names of the survey respondents
    official_names = list(set([row[0].strip().upper() for row in raw_rows]).union(set(official_names)))
    
# loop through the surveys, processing them one by one
for fname in FNAMES:
    raw_rows = read_csv(fname, ignoreheaders=args.ignoreheaders)

    row_labels = [row[0] for row in raw_rows]
    
    # Names in survey responses that were successfully matched to a UNIQUE respondent name
    matches = range(len(raw_rows))
    # Names in survey responses that were not matched to ANY respondent name
    nomatches = range(len(raw_rows))
    # Names in survey responses that were matched to MULTIPLE respondent name
    multimatches = range(len(raw_rows))
    # NAs
    nas = range(len(raw_rows))

    # Remove "none"-like reponses that indicate an empty list
    empty_terms = ['', 'None', 'none']

    def get_interp(names):
        clean_names = [x for x in [s.strip() for s in names] if x not in empty_terms]
        return [find_name_in_list(written_name, official_names, nicknames) for written_name in clean_names]

    # Split comma-delimited name-lists
    split_rows = copy.deepcopy(raw_rows)
    # Main loop
    for i in range(len(raw_rows)):
        print("Processing row %d" % i)
        s = raw_rows[i][1]
        matches[i] = []
        nomatches[i] = []
        multimatches[i] = []
        nas[i] = False
        if 'no comment' in s.lower():
            nas[i] = True
        elif 'nobody' in s.lower():
            continue
        else:
            # some important splitting possibilities:
            poss_splits = [
                # First Last; First Last; ...
                # Last, First; Last, First; ...
                s.strip().split(";"),
                # First Last, First Last, ...
                s.strip().split(","),
                # Last, First. Last, First. ...
                s.strip().split("."),
                # "Last, First" "Last, First" ...
                s.strip().split('\"')[1::2],
            ]
            ###
            # an interpretation of a survey response is a list of lists of possible name idxs
            # in an unambiguous interpretation, each list has length 1
            interps = [zip(names, get_interp(names)) for names in poss_splits]
            # best_interp maximizes number of unambiguous names
            best_interp = max(interps, key=lambda interp: sum([len(idxs) == 1 for (names, idxs) in interp]))
            # save results
            for (name, idxs) in best_interp:
                if len(idxs) == 1:
                    matches[i].append(idxs[0])
                elif len(idxs) == 0:
                    nomatches[i].append(name)
                elif len(idxs) > 1:
                    multimatches[i].append((name, idxs))

    # Save the match matrix        
    dense = []
    # import pdb; pdb.set_trace()
    for i in range(len(official_names)):
        if official_names[i] in row_labels:
            idx = row_labels.index(official_names[i])
            if nas[idx]:
                dense.append(['NA'] * len(official_names))
            else:
                dense.append([0] * len(official_names))
                for col in matches[idx]:
                    dense[i][col] = 1
        else:
            dense.append(['NA'] * len(official_names))
    
    basename = fname.split('.')[0]
    matrix2csv(basename + ".sociomatrix.csv", dense, official_names, official_names)
    errors2csv(basename + ".matches.csv", official_names, row_labels, raw_rows, nomatches, multimatches)

# save the nomatches
# print_errors(basename + ".failures.txt",multimatches,nomatches)
