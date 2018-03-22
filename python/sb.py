#!/usr/bin/python
from decimal import Decimal, ROUND_HALF_EVEN
dec0 = Decimal(0.00).quantize(Decimal('.01')) # Zero in currency format i.e. 0.00

# Function definitions
def validParentID ( parentID_in ):
    "This function converts supplied text to integer or None if blank"
    # parent_id = myDict[row][2]
    if parentID_in == '':
        parentID_out = None
    else:
        parentID_out = int(parentID_in)
    return parentID_out;

def validSpend ( spend_in ):
    "This function converts supplied value to decimal or None if zero"
    if spend_in == '0':
        spend_out = None
    else:
        spend_out = Decimal(myDict[row][3]).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN) or Decimal(0.00)
    return spend_out;

def incSpend ( spendPointer, spend_in):
    "This function adds spend_in to the spend at spendPointer"
    if spendPointer == None:
        spendPointer = spend_in
    else:   
        if spend_in is not None: 
            spendPointer += spend
    return;

# Read CSV file into myDict
import csv
rowno = 0
myDict = {}
with open("CWP.CSV", 'r') as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    for row in reader:
        myDict[rowno] = row
        rowno = rowno + 1
csvFile.close()

# Load myDict into myConsultants
myConsultants = {}
for row in myDict:
    consultant_id = int(myDict[row][0])
    name = myDict[row][1]
    parent_id = validParentID(myDict[row][2])
    spend = validSpend(myDict[row][3])
    downline_level1 = None
    downline_level2 = None
    # Check for duplicate consultant ID
    if consultant_id in myConsultants:
        print("Warning: duplicate consultant ID", consultant_id)
        if myConsultants[consultant_id][1] == None:
            myConsultants[consultant_id][1] = parent_id
        incSpend(myConsultants[consultant_id][2], spend)
    else:
        myConsultants[consultant_id] = [name, parent_id, spend, downline_level1, downline_level2]
    
# Compare number of rows against number of unique consultant IDs found
if len(myConsultants) != len(myDict):
    consultants = len(myConsultants)
    rows = len(myDict)
    print(consultants, "unique consultant IDs found (", rows, "rows imported)")

# Empty myDict
myDict = {}

# Add consultant spend to parent record
for key,value in myConsultants.items() :
    parent_id = value[1]
    spend = value[2]
    if parent_id is not None:
        if parent_id in myConsultants:
            if myConsultants[parent_id][3] == None:
                myConsultants[parent_id][3] = spend
            else:   
                if spend is not None: 
                    myConsultants[parent_id][3] += spend

# Add consultant downline spend to parent record
for key,value in myConsultants.items() :
    parent_id = value[1]
    downline_spend = value[3]
    if parent_id is not None:
        if parent_id in myConsultants:
            if myConsultants[parent_id][4] == None:
                myConsultants[parent_id][4] = downline_spend
            else:  
                if downline_spend is not None:  
                    myConsultants[parent_id][4] += downline_spend

# Replace None with blank / 0.00
for key,value in myConsultants.items() :
    if value[1] == None:
        value[1] = ''
    if value[2] == None:
        value[2] = dec0
    if value[3] == None:
        value[3] = dec0
    if value[4] == None:
        value[4] = dec0

# Output column headings
print("Consultant,Name,Parent,Spend,Level1,Level2")

total_spend = dec0
total_level1 = dec0
total_level2 = dec0

# Output results 
for key, value in myConsultants.items() :
    total_spend += value[2] 
    total_level1 += value[3]
    total_level2 += value[4]
    print ("{},{},{},{},{},{}".format(key, value[0], value[1], value[2],value[3],value[4]))

# Output totals
print ("Total spend         GBP {:,.2f}".format(total_spend))
print ("Total level 1 spend GBP {:,.2f}".format(total_level1))
print ("Total level 2 spend GBP {:,.2f}".format(total_level2))
