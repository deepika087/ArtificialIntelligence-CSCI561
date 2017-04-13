__author__ = 'deepika'

##This script will automatically run all test cases. And will report mismatches if any.

import hw3cs561s2017 as workflow #debug_
import os

directory = "newtestcases3" # Limit 13, for newtestcases limit is 11, for oldtestcases 7, newtestcases3 limit 13
limit = 13
basepath = os.path.dirname(__file__)
print basepath

count = 0
def compareFiles(index):

    #compare output.txt with respective output file
    fileName = 'output'
    if ( index < 10):
        fileName += "0" + str(index)
    else:
        fileName += str(index)
    fileName += ".txt"
    filepath = os.path.abspath(os.path.join(basepath, directory, fileName))

    data1 = []
    for line in open('output.txt'):
        data1.append(line.strip())

    data2 = []
    for line in open(filepath, 'r'):
        data2.append(line.strip())

    global count
    count = count + 1
    if (data1 == data2):
        print str(count) + "." +  " match", data1, data2
    else:
        print str(count) + "." +" Not matching ", data1, data2

if __name__ == "__main__":

    for i in range(1, limit):

        fileName = 'input'
        if ( i < 10):
            fileName += "0" + str(i)
        else:
            fileName += str(i)
        fileName += ".txt"
        filepath = os.path.abspath(os.path.join(basepath, directory, fileName))
        #print filepath
        workflow.main(filepath)

        compareFiles(i)


