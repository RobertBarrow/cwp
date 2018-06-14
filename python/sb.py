#!/usr/bin/python
from sys import argv # for reading in command line argument(s)
from os import path # for checking valid input filename
from csv import reader # for reading in input file (.CSV)
from enum import Enum, unique # for enumeration class

# Enumerations
@unique
class Column(Enum):
    ID = 0
    NAME = 1
    PARENT = 2
    SPEND = 3
    CURR = 4
    LEVEL = 5

@unique
class Position(Enum):
    NAME = 0
    PARENT_ID = 1
    SPEND = 2
    CURR = 3
    COUNT = 4
    LEVEL = 5
    RECOG = 6

# Global
DL_MAX = 10 # the maximum number of downline levels to calculate
REC_MAX = 5 # the number of levels in the recognition programme
DEBUG = [] # list of consultant IDs used for debugging purposes

# Function definitions
def validParentID ( validParentID_in ):
    """This function converts supplied text to integer or None if blank/"DIRECT"""
    if validParentID_in == '' or validParentID == "DIRECT": validParentID_out = None
    else: validParentID_out = int(validParentID_in)
    return validParentID_out

def add_DL ( add_DL_consultant_id, add_DL_generation, add_DL_spend, add_DL_count, add_DL_level, add_DL_recog ):
    """This function adds downline data to the parent consultant in myConsultants"""
    # add the downline's spend to the totals on the parent consultant (for add_DL_generation)
    if add_DL_spend is not None:
        myConsultants[add_DL_consultant_id][Position.SPEND.value][add_DL_generation] += add_DL_spend
    # add the downline to the headcount on the parent consultant (for add_DL_generation)
    if add_DL_count is not None:
        myConsultants[add_DL_consultant_id][Position.COUNT.value][0] += add_DL_count # total downline
        myConsultants[add_DL_consultant_id][Position.COUNT.value][add_DL_generation] += add_DL_count
    # add the downline level to the headcount on the parent consultant (for their recognition level)
    if add_DL_generation == 1:
        myConsultants[add_DL_consultant_id][Position.RECOG.value][0][add_DL_level] += 1
        myConsultants[add_DL_consultant_id][Position.RECOG.value][1][add_DL_level] += 1
    else:
        for z in range(REC_MAX): # loop through recognition levels for the current generational tier
            myConsultants[add_DL_consultant_id][Position.RECOG.value][0][z] += add_DL_recog[z]
            myConsultants[add_DL_consultant_id][Position.RECOG.value][add_DL_generation][z] += add_DL_recog[z]
    return

print(argv, len(argv)) # Just to DEBUG

# Check to see if any command line arguments have been supplied
if len(argv) > 1:
    # Check that sufficient command line arguments have been passed in 
    if len(argv)<3:
        print ("Fatal: You neeed to include both filenames as arguments to the command.")
        print ("Usage:  python %s <input filename> <output filename>" % argv[0])
        exit(1)

    # Use the supplied filenames
    input_file = argv[1] # Set the input file name to the first argument
    output_file = argv[2] # Set the output file name to the second argument
else:
    # Use the default names
    input_file = 'CWP.CSV' # default name for input file
    output_file = 'CWP_ANALYSIS.CSV' # default name for input file

# Check that the input file exists and read it into sourceData
if path.exists(input_file) and path.getsize(input_file) > 0:
    # Read CSV file into sourceData
    print("Reading in data from %s ..." % input_file)
    rowno = 0
    sourceData = {}
    with open(input_file, 'r') as csvFile:
        csvReader = reader(csvFile, delimiter=',')
        for row in csvReader:
            sourceData[rowno] = row
            rowno = rowno + 1
    csvFile.close()
else:
    print ("Error: input file %s does not exist or is inaccesible." % input_file)
    exit(1)

# Load sourceData into myConsultants
myConsultants = {}
for row in sourceData:
    if sourceData[row][Column.ID.value] != 'Consultant': # skip column headings
        consultant_id = int(sourceData[row][Column.ID.value])
        name = sourceData[row][Column.NAME.value]
        parent_id = validParentID(sourceData[row][Column.PARENT.value])
        spend = [float(0) for x in range(DL_MAX + 1)] # initialise spend array
        spend[0] = float(sourceData[row][Column.SPEND.value])
        curr = sourceData[row][Column.CURR.value]
        count = [int(0) for x in range(DL_MAX + 1)] # initialise count array
        count[0] = 1 # self
        level = int(sourceData[row][Column.LEVEL.value])
        # Check for invalid recognition levels
        if level < 0 or level > (REC_MAX):
            print("Error:", consultant_id, " has recognition level ", level, "!")
            level = 0 # to prevent subscript errors
        recog = [[int(0) for x in range(REC_MAX + 1)] for y in range(DL_MAX + 1)] # initialise recog array
        # recog[0][level] +=1 # add self to totals? // check with VTB
        # Check for duplicate consultant ID
        if consultant_id in myConsultants:
            print("Warning: duplicate consultant ID", consultant_id)
            if myConsultants[consultant_id][Position.PARENT_ID.value] == None:
                myConsultants[consultant_id][Position.PARENT_ID.value] = parent_id
            add_DL(consultant_id, 0, spend, 0, 0, [0,0,0,0,0,0])
        else:
            myConsultants[consultant_id] = [name, parent_id, spend, curr, count, level, recog]
    
# Compare number of rows against number of unique consultant IDs found
if len(myConsultants) != len(sourceData):
    consultants = len(myConsultants)
    rows = len(sourceData)
    print(consultants, "unique consultant IDs found (", rows, "rows imported)")

# Empty sourceData
sourceData = ''
          
# Add downline consultant data into to the parent record
for x in range(DL_MAX):
    downline_generation = x + 1
    for key,record in myConsultants.items() :
        parent_id = record[Position.PARENT_ID.value]
        if parent_id is not None and parent_id in myConsultants:
            downline_spend = record[Position.SPEND.value][x]
            downline_count = record[Position.COUNT.value][x]
            downline_level = record[Position.LEVEL.value]
            downline_recog = record[Position.RECOG.value][x] # headcount of each recog level for current gen 
            add_DL(parent_id, downline_generation, downline_spend, downline_count, downline_level, downline_recog)
            if key in DEBUG or parent_id in DEBUG: # OUTPUT FOR DEBUG PURPOSES
                print(x, key, downline_level, downline_recog, 0,\
                    myConsultants[parent_id][Position.RECOG.value][0], downline_generation, \
                    myConsultants[parent_id][Position.RECOG.value][downline_generation], parent_id)

# Initialise totals
total_spend = [float(0) for x in range(DL_MAX + 1)]

# Output spend data to SPEND.CSV file
print("Outputting data to %s ..." % output_file)
with open(output_file, 'w') as CWP_ANALYSIS:
    # Main column headings
    CWP_ANALYSIS.write("Consultant,Name,Parent,Currency,Recog_level,Spend,")
    # Spend 1st to 3rd gen
    CWP_ANALYSIS.write("Spend_1st_gen,Spend_2nd_gen,Spend_3rd_gen")
    # Spend 4th to 20th gen
    for x in range(4, DL_MAX + 1):
        CWP_ANALYSIS.write(",Spend_{}th_gen".format(x))
    # Teamsize 1st to 3rd gen
    CWP_ANALYSIS.write(",Teamsize_1st_gen,Teamsize_2nd_gen,Teamsize_3rd_gen")
    # Teamsize 4th to 20th gen
    for x in range(4, DL_MAX + 1):
        CWP_ANALYSIS.write(",Teamsize_{}th_gen".format(x))
    # total number of consultants at each recognition level
    for x in range(REC_MAX + 1):
        CWP_ANALYSIS.write(",Recog_level_{}".format(x))
    # number of consultants at each recognition level in 1st generation
    for x in range(REC_MAX + 1):
        CWP_ANALYSIS.write(",1st_gen_Recog_level_{}".format(x))
    # number of consultants at each recognition level in 2nd generation
    for x in range(REC_MAX + 1):
        CWP_ANALYSIS.write(",2nd_gen_Recog_level_{}".format(x))
    # number of consultants at each recognition level in 3rd generation
    for x in range(REC_MAX + 1):
        CWP_ANALYSIS.write(",3rd_gen_Recog_level_{}".format(x))
    # number of consultants at each recognition level in 4th generation
    for x in range(REC_MAX + 1):
        CWP_ANALYSIS.write(",4th_gen_Recog_level_{}".format(x))
    # newline
    CWP_ANALYSIS.write("\n")
    # Rows
    for key, record in myConsultants.items() :
        # Tidy up ParentID (replace <None> with <blank>) and output ID, Name and ParentID 
        if record[Position.PARENT_ID.value] == None: record[Position.PARENT_ID.value] = ''
        CWP_ANALYSIS.write("{},\"{}\",{},\"{}\",{}".format(key, record[Position.NAME.value], \
            record[Position.PARENT_ID.value],record[Position.CURR.value],record[Position.LEVEL.value]))
        # Update total_spend array and output spend values for each generation
        for x in range(0, DL_MAX + 1):
            total_spend[x] += record[Position.SPEND.value][x]
            CWP_ANALYSIS.write(",{:.2f}".format(round(record[Position.SPEND.value][x], 2)))
        # Output number of consultants in each generation (tier) 
        for x in range(1, DL_MAX + 1):
            CWP_ANALYSIS.write(",{}".format((record[Position.COUNT.value][x])))
        # Output total number of consultants at each recognition level
        for x in range(REC_MAX + 1):
            CWP_ANALYSIS.write(",{}".format((record[Position.RECOG.value][0][x])))
        # Output number of consultants at each recognition level for first four generations (1 to 4)
        for x in range(1, 5):
            for y in range(REC_MAX + 1):
                CWP_ANALYSIS.write(",{}".format((record[Position.RECOG.value][x][y])))
        # Newline
        CWP_ANALYSIS.write("\n")
# Close CWP_ANALYSIS.CSV file        
CWP_ANALYSIS.close()

# Output totals ( stdout )
print ("Number of consultants   {}".format(len(myConsultants)))
for x in range(0, DL_MAX + 1):
    print ("Total spend level {} GBP {:,.2f}".format(x, total_spend[x]))
