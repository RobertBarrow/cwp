#!/usr/bin/python
import json # for storing data in json format
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
        if myConsultants[addSpend_consultant_id][2][addSpend_level] == None:
            myConsultants[addSpend_consultant_id][2][addSpend_level] = addSpend_in
        else:   
            myConsultants[addSpend_consultant_id][2][addSpend_level] += addSpend_in
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
    consultant_id = int(sourceData[row][0])
    name = sourceData[row][1]
    parent_id = validParentID(sourceData[row][2])
    
    spend = [validSpend(sourceData[row][3])] #, None, None, None]
    for x in range(1, MAX + 1):
        spend.append(None)

    # Check for duplicate consultant ID
    if consultant_id in myConsultants:
        print("Warning: duplicate consultant ID", consultant_id)
        if myConsultants[consultant_id][1] == None:
            myConsultants[consultant_id][1] = parent_id
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
        parent_id = value[1]
        if parent_id is not None and parent_id in myConsultants:
            downline_spend = value[2][x]
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
out.write("Consultant,Name,Parent,Spend,Level1,Level2,Level3\n")
# Rows
for key, value in myConsultants.items() :
    # Tidy up ParentID (replace <None> with <blank>) and output ID, Name and ParentID 
    if value[1] == None: value[1] = ''
    out.write("{},\"{}\",{}".format(key, value[0], value[1]))
    # Tidy up Spend array (replace <None>'s with 0.00's), add to total_spend array and output 
    for x in range(0, MAX):
        if value[2][x] == None: value[2][x] = 0.00
        total_spend[x] += value[2][x]
        out.write(",{}".format(round(value[2][0], 2)))
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