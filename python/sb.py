#!/usr/bin/python
import json # for storing data in json format

SOURCE_ID_COLUMN = 0
SOURCE_NAME_COLUMN = 1
SOURCE_PARENT_COLUMN = 2
SOURCE_SPEND_COLUMN = 3

NAME = 0
PARENT_ID = 1
SPEND_ARRAY = 2

MAX = 10 # should be 1 + the maximum number of downline levels to calculate

# Function definitions
def validParentID ( validParentID_in ):
    "This function converts supplied text to integer or None if blank"
    if validParentID_in == '': validParentID_out = None
    else: validParentID_out = int(validParentID_in)
    return validParentID_out

def validSpend ( spend_in ):
    "This function converts supplied value to float or None if zero"
    if spend_in == '0': spend_out = None
    else: spend_out = float(spend_in) or 0.0
    return spend_out

def addSpend ( addSpend_consultant_id, addSpend_level, addSpend_in):
    "Adds addSpend_in to addSpend_level for addSpend_consultant_id in myConsultants"
    if addSpend_in is not None:
        if myConsultants[addSpend_consultant_id][SPEND_ARRAY][addSpend_level] == None:
            myConsultants[addSpend_consultant_id][SPEND_ARRAY][addSpend_level] = addSpend_in
        else:   
            myConsultants[addSpend_consultant_id][SPEND_ARRAY][addSpend_level] += addSpend_in
    return

# Read CSV file into sourceData
import csv
rowno = 0
sourceData = {}
with open("CWP.CSV", 'r') as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    for row in reader:
        sourceData[rowno] = row
        rowno = rowno + 1
csvFile.close()

# Save input data in json format
with open('in_data.json', 'w') as in_data:
    json.dump(sourceData, in_data)
in_data.close()


# Load sourceData into myConsultants
myConsultants = {}
for row in sourceData:
    consultant_id = int(sourceData[row][SOURCE_ID_COLUMN])
    name = sourceData[row][SOURCE_NAME_COLUMN]
    parent_id = validParentID(sourceData[row][SOURCE_PARENT_COLUMN])
    spend = [validSpend(sourceData[row][SOURCE_SPEND_COLUMN])]
    for x in range(1, MAX + 1): # Initialise array
        spend.append(None)

    # Check for duplicate consultant ID
    if consultant_id in myConsultants:
        print("Warning: duplicate consultant ID", consultant_id)
        if myConsultants[consultant_id][PARENT_ID] == None:
            myConsultants[consultant_id][PARENT_ID] = parent_id
        addSpend(consultant_id, 0, spend)
    else:
        myConsultants[consultant_id] = [name, parent_id, spend]
    
# Compare number of rows against number of unique consultant IDs found
if len(myConsultants) != len(sourceData):
    consultants = len(myConsultants)
    rows = len(sourceData)
    print(consultants, "unique consultant IDs found (", rows, "rows imported)")

# Empty sourceData
sourceData = ''
          
# Add consultant downline spend to parent record
for x in range(0, MAX):
    for key,value in myConsultants.items() :
        parent_id = value[PARENT_ID]
        if parent_id is not None and parent_id in myConsultants:
            downline_spend = value[SPEND_ARRAY][x]
            if downline_spend is not None:
                y = x + 1
                addSpend(parent_id, y, downline_spend)

# Initialise totals
total_spend = []
for x in range(0, MAX):
    total_spend.append(float(0))

# Output results to OUT.CSV
out = open("OUT.CSV", 'w')
# Column headings
out.write("Consultant,Name,Parent,Spend")
for x in range(1, MAX):
    out.write(",Level_{}".format(x))
out.write("\n")
# Rows
for key, value in myConsultants.items() :
    # Tidy up ParentID (replace <None> with <blank>) and output ID, Name and ParentID 
    if value[PARENT_ID] == None: value[PARENT_ID] = ''
    out.write("{},\"{}\",{}".format(key, value[NAME], value[PARENT_ID]))
    # Tidy up Spend array (replace <None>'s with 0.00's), add to total_spend array and output 
    for x in range(0, MAX):
        if value[SPEND_ARRAY][x] == None: value[SPEND_ARRAY][x] = 0.00
        total_spend[x] += value[SPEND_ARRAY][x]
        out.write(",{}".format(round(value[SPEND_ARRAY][x], 2)))
    # Newline
    out.write("\n")
# Close OUT.CSV file        
out.close()

# Save output data in json format
with open('out_data.json', 'w') as out_data:
    json.dump(myConsultants, out_data)
out_data.close()

# Output totals ( stdout )
print ("Number of consultants   {}".format(len(myConsultants)))
for x in range(0, MAX):
    print ("Total spend level {} GBP {:,.2f}".format(x, total_spend[x]))