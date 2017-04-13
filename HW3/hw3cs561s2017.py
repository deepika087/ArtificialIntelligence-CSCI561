__author__ = 'deepika'

import math
import sys

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class ProbDist:
    def __init__(self, varname='?', freqs=None):
        """If freqs is given, it is a dictionary of values - frequency pairs,
        then ProbDist is normalized."""
        self.prob = {}
        self.varname = varname
        self.values = []
        if freqs:
            for (v, p) in freqs.items():
                self[v] = p
            self.normalize()

    def normalize(self):
        """Make sure the probabilities of all values sum to 1.
        Returns the normalized distribution.
        Raises a ZeroDivisionError if the sum of the values is 0."""
        total = sum(self.prob.values())
        if not isclose(total, 1.0):
            for val in self.prob:
                self.prob[val] /= total
        return self

    def show_approx(self, numfmt='{:.3g}'):
        """Show the probabilities rounded and sorted by key, for the
        sake of portable doctests."""
        return ', '.join([('{}: ' + numfmt).format(v, p)
                          for (v, p) in sorted(self.prob.items())])


class Factor:
    """A factor in a joint distribution."""

    def __init__(self, variables, cpt):
        self.variables = variables
        self.cpt = cpt

    def pointwise_product(self, other, bn):
        """Multiply two factors, combining their variables."""
        variables = list(set(self.variables) | set(other.variables))
        cpt = {event_values(e, variables): self.p(e) * other.p(e)
               for e in all_events(variables, bn, {})}
        return Factor(variables, cpt)

    def sum_out(self, var, bn):
        """Make a factor eliminating var by summing over its values."""
        variables = [X for X in self.variables if X != var]
        cpt = {event_values(e, variables): sum(self.p(extend(e, var, val))
                                               for val in [0, 1])
               for e in all_events(variables, bn, {})}
        return Factor(variables, cpt)

    def normalize(self):
        """Return my probabilities; must be down to one variable."""
        #assert len(self.variables) == 1
        return ProbDist(self.variables[0],
                        {k: v for ((k,), v) in self.cpt.items()})

    def p(self, e):
        """Look up my value tabulated for e."""
        return self.cpt[event_values(e, self.variables)]

    def __repr__(self):
        return str(self.variables) + " " + str(self.cpt)

    def __str__(self):
        return self.__repr__()

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

            if ('|' in line):
                line = line.split('|')
                query = line[0].strip().split(', ')
                conditions = line[1].strip().split(', ')
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
        p = enumeration_all(table_data['all_vars'], queries, table_data)
        #print " receeived p = ", p
    else:
        p = enumeration_ask(queries, conditions, table_data)
    return p

def extend(s, var, val):
    s2 = s.copy()
    s2[var] = val
    return s2

def all_events(variables, table_data, evidence):
    if not variables:
        yield evidence
    else:
        X, rest = variables[0], variables[1:]
        for e1 in all_events(rest, table_data, evidence):
            for x in [0, 1]:
                yield extend(e1, X, x)

def event_values(event, variables):

    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    else:
        return tuple([event[var] for var in variables])

def make_factor(var, evidence, table_data):
    node = table_data[var]
    variables = [X for X in [var] + node.parents if X not in evidence]
    #print "variables = ", variables

    cpt = {event_values(e1, variables): node.p(e1[var], e1)
           for e1 in all_events(variables, table_data, evidence)}
    return Factor(variables, cpt)

def is_hidden(var, queries, conditions):
    #print var, queries, conditions
    return var not in queries or var not in conditions

def pointwise_product(factors, bn):
    return reduce(lambda f, g: f.pointwise_product(g, bn), factors)

def sum_out(var, factors, bn):
    result, var_factors = [], []
    for f in factors:
        (var_factors if var in f.variables else result).append(f)

    if (len(var_factors) > 0):
        fact = pointwise_product(var_factors, bn)
        if (isinstance(fact, Factor)):
            result.append(fact.sum_out(var, bn))
    return result

#this function will receive probabilities of the form P(A,B,C)
def enumeration_all(queries, conditions, table_data):
    factors = []
    for var in reversed(table_data['all_vars']):
        result = make_factor(var, conditions, table_data)
        factors.append(result)
        if is_hidden(var, queries, conditions):
            factors = sum_out(var, factors, table_data)
    result = pointwise_product(factors, table_data)

    return result.cpt.values()[0]

# This function will be called when probability is of the form P(A,B|C,D)
# in which case compute P(A,B,C,D)/P(C,D). Hence numerator as well as denominator will call
# enumeration_all individually.
def enumeration_ask(queries, conditions, table_data):

    queries.update(conditions)
    numerator = enumeration_all(table_data['all_vars'], queries, table_data)
    denominator = enumeration_all(table_data['all_vars'], conditions, table_data)
    if (denominator == 0):
        return 0.0
    else:
        return numerator/denominator

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

    eu = 0
    for i in range(2**len(utility.parents)):
        queryUpdated = relevantNodes(utility.parents, i)

        conditionsUpdated = dict(queries)
        conditionsUpdated.update(conditions)
        eu += utility.prob_table[i]*handleProbability(queryUpdated, conditionsUpdated, table_data)
    return eu

def handleMaximumUtility(utility, queries, conditions, table):

    maxEU = -sys.maxint
    maxEU_Index = None
    for i in range(2**len(queries)):
        queriesUpdated = relevantNodes(queries, i)

        eu = handleUtility(utility, queriesUpdated, conditions, table)
        if (eu > maxEU):
            maxEU=eu
            maxEU_Index=i
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

        #print "Fetching index = ", index, " from ", self.prob_table
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
    table_lines, problems, utility = Parse.parseLines(fileName)

    table = KB.parse(table_lines)
    #print table
    problems = Problem.parse(problems)
    #print problems
    utility = Node.parse(utility)
    #print utility

    target = open('output.txt', 'w+')

    for problem in problems:
        if (problem.type == 'P'):
            #print " Problem : ", problem
            result = handleProbability(problem.queries, problem.conditions, table)
            result = my_round(result, 2)
            target.write(str(format(result, '.2f')) + "\n")
            #print "Write probability", format(result, '.2f')
        elif (problem.type == 'EU'):
            #print " Problem : ", problem
            result = handleUtility(utility, problem.queries, problem.conditions, table)
            result = int(( result * 100 ) + 0.5) / float(100)
            format(result, '.2f')
            if (result < int(result) + 0.50):
                target.write( str(int(math.floor(result))) + "\n")
            else:
                target.write( str(int(math.ceil(result))) + "\n")
        else:
            #print " Handle MEU"
            #print " Problem : ", problem
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