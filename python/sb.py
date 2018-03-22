#!/usr/bin/python
import json # for storing data in json format

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

def addSpend ( addSpend_consultant_id, addSpend_pointer, addSpend_in):
    "Adds addSpend_in to addSpend_Pointer for addSpend_consultant_id in myConsultants"
    if addSpend_in is not None:          
        if myConsultants[addSpend_consultant_id][addSpend_pointer] == None:
            myConsultants[addSpend_consultant_id][addSpend_pointer] = addSpend_in
        else:   
            myConsultants[addSpend_consultant_id][addSpend_pointer] += addSpend_in
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
    spend = validSpend(sourceData[row][3])
    downline_level1 = None
    downline_level2 = None
    # Check for duplicate consultant ID
    if consultant_id in myConsultants:
        print("Warning: duplicate consultant ID", consultant_id)
        if myConsultants[consultant_id][1] == None:
            myConsultants[consultant_id][1] = parent_id
        addSpend(consultant_id, 2, spend)
    else:
        myConsultants[consultant_id] = [name, parent_id, spend, downline_level1, downline_level2]
    
# Compare number of rows against number of unique consultant IDs found
if len(myConsultants) != len(sourceData):
    consultants = len(myConsultants)
    rows = len(sourceData)
    print(consultants, "unique consultant IDs found (", rows, "rows imported)")

# Empty sourceData
sourceData = ''

# Add consultant spend to parent record
for key,value in myConsultants.items() :
    parent_id = value[1]
    spend = value[2]
    if parent_id is not None and parent_id in myConsultants: addSpend(parent_id, 3, spend)
            
# Add consultant downline spend to parent record
for key,value in myConsultants.items() :
    parent_id = value[1]
    downline_spend = value[3]
    if parent_id is not None and parent_id in myConsultants: addSpend(parent_id, 4, downline_spend)

# Tidy up : replace <None> with <blank> / 0.00 and round floats to 2dp
for key,value in myConsultants.items() :
    if value[1] == None: value[1] = ''
    if value[2] == None: value[2] = 0.00
    else: value[2] = round(value[2], 2)
    if value[3] == None: value[3] = 0.00
    else: value[3] = round(value[3], 2)
    if value[4] == None: value[4] = 0.00
    else: value[4] = round(value[4], 2)

# Initialise totals
total_spend = float(0)
total_level1 = float(0)
total_level2 = float(0)

# Output results to OUT.CSV
out = open("OUT.CSV", 'w')
out.write("Consultant,Name,Parent,Spend,Level1,Level2\n")

for key, value in myConsultants.items() :
    # Tidy up : replace <None> with <blank> / 0.00
    if value[1] == None: value[1] = ''
    if value[2] == None: value[2] = 0.00
    if value[3] == None: value[3] = 0.00
    if value[4] == None: value[4] = 0.00
    out.write("{},\"{}\",{},{},{},{}\n".format(key, value[0], value[1], round(value[2], 2), 
        round(value[3], 2), round(value[4], 2) ))
    # Add to totals
    total_spend += value[2]
    total_level1 += value[3]
    total_level2 += value[4]
    
out.close()

# Save output data in json format
with open('out_data.json', 'w') as out_data:
    json.dump(myConsultants, out_data)
out_data.close()

# Output totals ( stdout )
print ("Number of consultants   {}".format(len(myConsultants)))
print ("Total spend         GBP {:,.2f}".format(total_spend))
print ("Total level 1 spend GBP {:,.2f}".format(total_level1))
print ("Total level 2 spend GBP {:,.2f}".format(total_level2))
