#!/usr/bin/python
import csv # for reading in source CWP.CSV source file
from enum import Enum, unique # For enumeration class

# Enumerations
@unique
class Column(Enum):
    ID = 0
    NAME = 1
    PARENT = 2
    SPEND = 3

@unique
class Position(Enum):
    NAME = 0
    PARENT_ID = 1
    SPEND = 2
    COUNT = 3

# Global
_MAX = 10 # should be 1 + the maximum number of downline levels to calculate

# Function definitions
def validParentID ( validParentID_in ):
    """This function converts supplied text to integer or None if blank/"DIRECT"""
    if validParentID_in == '' or validParentID == "DIRECT": validParentID_out = None
    else: validParentID_out = int(validParentID_in)
    return validParentID_out

def add_DL ( add_DL_consultant_id, add_DL_level, add_DL_spend, add_DL_count ):
    """This function adds add_DL_spend/count to add_DL_level for add_DL_consultant_id in myConsultants"""
    if add_DL_spend is not None:
        myConsultants[add_DL_consultant_id][Position.SPEND.value][add_DL_level] += add_DL_spend
    if add_DL_count is not None:
        myConsultants[add_DL_consultant_id][Position.COUNT.value][0] += add_DL_count # total downline
        myConsultants[add_DL_consultant_id][Position.COUNT.value][add_DL_level] += add_DL_count
    return

# Read CSV file into sourceData
rowno = 0
sourceData = {}
with open("CWP.CSV", 'r') as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    for row in reader:
        sourceData[rowno] = row
        rowno = rowno + 1
csvFile.close()

# Load sourceData into myConsultants
myConsultants = {}
for row in sourceData:
    consultant_id = int(sourceData[row][Column.ID.value])
    name = sourceData[row][Column.NAME.value]
    parent_id = validParentID(sourceData[row][Column.PARENT.value])
    spend = [float(0) for x in range(_MAX + 1)] # initialise spend array
    spend[0] = float(sourceData[row][Column.SPEND.value])
    count = [int(0) for x in range(_MAX + 1)] # initialise count array
    count[0] = 1 # self

    # Check for duplicate consultant ID
    if consultant_id in myConsultants:
        print("Warning: duplicate consultant ID", consultant_id)
        if myConsultants[consultant_id][Position.PARENT_ID.value] == None:
            myConsultants[consultant_id][Position.PARENT_ID.value] = parent_id
        addSpend(consultant_id, 0, spend, 0)
    else:
        myConsultants[consultant_id] = [name, parent_id, spend, count]
    
# Compare number of rows against number of unique consultant IDs found
if len(myConsultants) != len(sourceData):
    consultants = len(myConsultants)
    rows = len(sourceData)
    print(consultants, "unique consultant IDs found (", rows, "rows imported)")

# Empty sourceData
sourceData = ''
          
# Add consultant downline spend to parent record
for x in range(_MAX):
    y = x + 1
    for key,record in myConsultants.items() :
        parent_id = record[Position.PARENT_ID.value]
        if parent_id is not None and parent_id in myConsultants:
            downline_spend = record[Position.SPEND.value][x]
            downline_count = record[Position.COUNT.value][x]
            add_DL(parent_id, y, downline_spend, downline_count)

# Initialise totals
total_spend = [float(0) for x in range(_MAX)]

# Output spend data to SPEND.CSV file
with open("SPEND.CSV", 'w') as spend_csv:
    # Column headings
    spend_csv.write("Consultant,Name,Parent,Spend")
    for x in range(1, _MAX):
        spend_csv.write(",Level_{}".format(x))
    spend_csv.write("\n")
    # Rows
    for key, record in myConsultants.items() :
        # Tidy up ParentID (replace <None> with <blank>) and output ID, Name and ParentID 
        if record[Position.PARENT_ID.value] == None: record[Position.PARENT_ID.value] = ''
        spend_csv.write("{},\"{}\",{}".format(key, record[Position.NAME.value], record[Position.PARENT_ID.value]))
        # Update total_spend array and output values
        for x in range(0, _MAX):
            total_spend[x] += record[Position.SPEND.value][x]
            spend_csv.write(",{:.2f}".format(round(record[Position.SPEND.value][x], 2)))
        # Newline
        spend_csv.write("\n")
# Close SPEND.CSV file        
spend_csv.close()

# Output count data to COUNT.CSV file
with open("COUNT.CSV", 'w') as count_csv:
    # Column headings
    count_csv.write("Consultant,Name,Parent")
    for x in range(1, _MAX):
        count_csv.write(",Level_{}".format(x))
    count_csv.write("\n")
    # Rows
    for key, record in myConsultants.items() :
        # Tidy up ParentID (replace <None> with <blank>) and output ID, Name and ParentID 
        if record[Position.PARENT_ID.value] == None: record[Position.PARENT_ID.value] = ''
        count_csv.write("{},\"{}\",{}".format(key, record[Position.NAME.value], record[Position.PARENT_ID.value]))
        # output counts
        for x in range(1, _MAX):
            count_csv.write(",{}".format((record[Position.COUNT.value][x])))
        # Newline
        count_csv.write("\n")
# Close COUNT.CSV file        
count_csv.close()

# Output totals ( stdout )
print ("Number of consultants   {}".format(len(myConsultants)))
for x in range(0, _MAX):
    print ("Total spend level {} GBP {:,.2f}".format(x, total_spend[x]))