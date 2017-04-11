__author__ = 'deepika'

import copy
import math
import sys
import logging
logging.basicConfig(filename='bayesian.log',level=logging.DEBUG)

def my_round(data, precise):

    sign = True if data < 0 else False
    updated_data = -data if sign else data
    updated_data = updated_data + 1e-8
    decimal = updated_data - int(updated_data)
    num = int (decimal* (10**(precise+1)))
    if num % 10 >= 5:
        num += 10
    num = num/10
    result = num/(10.0**(precise)) + int(updated_data)
    return -result if sign else result

class Parse:

    @staticmethod
    def parseLines(fileName):

        table_lines = []
        problems = []
        utilities = []

        count = 0
        for line in open(fileName):
            line = line.strip()

            if (line == "******"):
                count += 1
                continue

            if (count == 0):
                problems.append(line)

            if (count == 1):
                table_lines.append(line)

            if (count == 2):
                utilities.append(line)
        return table_lines, problems, utilities

    @staticmethod
    def index(line):
        seq = 0
        for mark in line:
            seq = (seq<<1) + (1 if mark.strip() =='+' else 0)
        return seq

class Problem(object):

    # Type can be P, EU, MEU
    # Query will be the part before |. Can be a list(in case of MEU) of dictionary
    # Condition will be the part after |. In dictionary
    def __init__(self, type, queries, conditions):
        self.type = type
        if (self.type == 'MEU'):
            self.queries = queries
        else:
            self.queries = {}
            for _ in queries:
                _ = _.split(' = ')
                self.queries[_[0]] = 1 if _[1] == '+' else 0

        self.conditions = {}
        for _ in conditions:
            _ = _.split(' = ')
            self.conditions[_[0]] = 1 if _[1] == '+' else 0

    @classmethod
    def parse(cls, lines):

        problems = list()

        for line in lines:
            task_type = None
            if (line.startswith('P')):
                line = line[2:len(line)-1]
                task_type = 'P'
            elif (line.startswith('EU')):
                line = line[3:len(line)-1]
                task_type = 'EU'
            elif (line.startswith('MEU')):
                line = line[4:len(line)-1]
                task_type = 'MEU'

            if (' | ' in line):
                line = line.split(' | ')
                query = line[0].split(', ')
                conditions = line[1].split(', ')
            else:
                query = line.split(', ')
                conditions = []
            problems.append(cls(task_type, query, conditions))
        return problems

    def __repr__(self):
        return "[" + self.type + " | " + str(self.queries) + " | "  + str(self.conditions) +"]\n"

    def __str__(self):
        return self.__repr__()

def contraCheck(queries, conditions):

    for key in queries.keys():
        if key in conditions.keys():
            if (queries[key] != conditions[key]):
                return True
    return False

def handleProbability(queries, conditions, table_data):
    if (contraCheck(queries, conditions)):
        return 0.0
    p = 0.0
    if (len(conditions) == 0): #probability of the for P(A, B, C) or P(A) then do enumeration_all directly
        logging.debug(" Calling all with evidence : " + str(queries))
        p = enumeration_all(table_data['all_vars'], queries, table_data)
    else:
        logging.debug(" Calling ask with queries and conditions : " + str(queries) + str(conditions))
        p = enumeration_ask(queries, conditions, table_data)
    return p

def enumeration_all(queries, conditions, table_data):
    logging.debug( " find prob of  : " + str(queries) + "given conditions"+ str(conditions))
    if not queries:
        return 1.0
    Y, rest = queries[0], queries[1:]
    YNode = table_data[Y]

    #Taken from AIMA pseudo code as given on github
    if Y in conditions.keys():
        return YNode.p(conditions[Y], conditions) * enumeration_all(queries[1:], conditions, table_data)
    else:
        ey_true = copy.copy(conditions)
        ey_true[Y] = 1
        ey_false = copy.copy(conditions)
        ey_false[Y] = 0
        return YNode.p(1, conditions) * enumeration_all(queries[1:], ey_true, table_data) + YNode.p(0, conditions) * enumeration_all(queries[1:], ey_false, table_data)

# This function will be called when probability is of the form P(A,B|C,D)
# in which case compute P(A,B,C,D)/P(C,D). Hence numerator as well as denominator will call
# enumeration_all individually.
def enumeration_ask(queries, conditions, table_data):

    queries.update(conditions)
    return enumeration_all(table_data['all_vars'], queries, table_data)/enumeration_all(table_data['all_vars'], conditions, table_data)

def relevantNodes(parents, i):
    length, re_list = len(parents), list(parents)
    temp = i
    re_list.reverse()
    if (2**length-1) < i:
        return None
    result = dict()
    for key in re_list:
        result[key] = temp%2
        temp = temp /2
    return result

def handleUtility(utility, queries, conditions, table_data):

    print " EU "
    eu = 0
    for i in range(2**len(utility.parents)):
        queryUpdated = relevantNodes(utility.parents, i)

        conditionsUpdated = dict(queries)
        conditionsUpdated.update(conditions)
        print queryUpdated, conditionsUpdated
        eu += utility.prob_table[i]*handleProbability(queryUpdated, conditionsUpdated, table_data)
    return eu

def handleMaximumUtility(utility, queries, conditions, table):
    print "MEU"
    print " Queries : ", queries
    maxEU = -sys.maxint
    maxEU_Index = None
    for i in range(2**len(queries)):
        queriesUpdated = relevantNodes(queries, i)

        eu = handleUtility(utility, queriesUpdated, conditions, table)
        if (eu > maxEU):
            maxEU=eu
            maxEU_Index=i
        #resultTemp = indexToNodes(i, len(queries))
        #print ' '.join(resultTemp), eu
    result = indexToNodes(maxEU_Index, len(queries))

    return ' '.join(result), maxEU

# Nodes not required becuase all we have to send is + - - and so on
# not for which particular nodes
def indexToNodes(index, length):
    if index > (2**length-1):
        return None
    result, tmp = list(), index
    for i in xrange(length-1, -1, -1):
        flag = tmp >> i
        result.append('+' if flag else '-')
        tmp = tmp - flag* 2**i
    return result

class Node(object):

    def __init__(self, name, parents, prob_table):
        self.name = name
        if (isinstance(parents, list)):
            self.parents = parents
        else:
            self.parents = [parents]
        self.prob_table = prob_table

    @classmethod
    def parse(cls, lines):

        if (len(lines) == 0):
            #print " don't send zero number of lines to Node class"
            return None

        #Find Name and parents
        name = lines[0].split(' | ')[0].strip()

        if ' | ' in lines[0]:
            parents = lines[0].split(' | ')[1].split()
        else:
            parents = []
        if lines[1].strip() == 'decision':
            return cls(name=name, parents=parents, prob_table=None)

        #If reached here then lines are of the form 0.3 + +
        if (len(parents) > 0):
            prob_table = [0 for _ in range(2**len(parents))]
            lines = lines[1:] #relevant probabilities
            for _ in lines:
                _ = _.split()
                prob_table[Parse.index(_[1:])] = float(_[0])
            return cls(name, parents, prob_table)
        else:
            return cls(name, parents, [ float(lines[1]) ])

    def __repr__(self):
        return "[" + self.name + " | " +str(self.parents) + " | " + str(self.prob_table) + "]\n"

    def __str__(self):
        return self.__repr__()

    def p(self, sign, evidence):
        if (self.prob_table is None):
            return 1.0

        index = 0
        for parent in self.parents:
            index = (index<<1) + evidence[parent]

        if (sign == 1):
            return self.prob_table[index]
        else:
            return 1 - self.prob_table[index]

class KB:

    @staticmethod
    def parse(table_lines):
        table = dict()
        data = []
        count = 0
        table['all_vars'] = [] #Created this array because table.keys() returns variables such that child occurs before parent
        for line in table_lines:
            line = line.strip()
            count = count + 1

            if (line != "***" or count == len(table_lines)):
                data.append(line)

            if (line == "***" or count == len(table_lines)):
                node = Node.parse(data)
                data = []
                table[node.name] = node
                table['all_vars'].append(node.name)
        return table

def main(fileName):
    print "XYZ"
    table_lines, problems, utility = Parse.parseLines(fileName)

    table = KB.parse(table_lines)
    problems = Problem.parse(problems)
    utility = Node.parse(utility)

    target = open('output.txt', 'w+')

    for problem in problems:
        if (problem.type == 'P'):
            result = handleProbability(problem.queries, problem.conditions, table)
            result = my_round(result, 2)
            target.write(str(format(result, '.2f')) + "\n")
        elif (problem.type == 'EU'):
            result = handleUtility(utility, problem.queries, problem.conditions, table)
            result = int(( result * 100 ) + 0.5) / float(100)
            format(result, '.2f')
            if (result < int(result) + 0.50):
                target.write( str(int(math.floor(result))) + "\n")
            else:
                target.write( str(int(math.ceil(result))) + "\n")
        else:
            #print " Handle MEU"
            resultTuple =  handleMaximumUtility(utility, problem.queries, problem.conditions, table)
            result = resultTuple[1]
            result = int(( result * 100 ) + 0.5) / float(100)
            format(result, '.2f')
            if (result < int(result) + 0.50):
                result = int(math.floor(result))
            else:
                result = int(math.ceil(result))
            target.write( resultTuple[0] + " " + str(result) + "\n" )

if __name__ == "__main__":
    fileName='input.txt'
    main(fileName)
