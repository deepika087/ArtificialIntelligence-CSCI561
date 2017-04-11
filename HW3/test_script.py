__author__ = 'deepika'

##This script will automatically run all test cases. And will report mismatches if any.

import hw3cs561s2017 as workflow #debug_
import os

basepath = os.path.dirname(__file__)
print basepath

def compareFiles(index):

    #compare output.txt with respective output file
    fileName = 'output'
    if ( index < 10):
        fileName += "0" + str(index)
    else:
        fileName += str(index)
    fileName += ".txt"
    filepath = os.path.abspath(os.path.join(basepath, "newtestcases", fileName))

    data1 = []
    for line in open('output.txt'):
        data1.append(line.strip())

    data2 = []
    for line in open(filepath, 'r'):
        data2.append(line.strip())

    if (data1 == data2):
        print " match", data1, data2
    else:
        print " Not matching ", data1, data2

if __name__ == "__main__":

    for i in range(1, 11):

        fileName = 'input'
        if ( i < 10):
            fileName += "0" + str(i)
        else:
            fileName += str(i)
        fileName += ".txt"
        filepath = os.path.abspath(os.path.join(basepath, "newtestcases", fileName))
        workflow.main(filepath)

        compareFiles(i)


