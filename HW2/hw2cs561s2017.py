__author__ = 'deepika'

import copy
import sys
import random

setOfClauses = dict()
GLOBAL_CLAUSE_COUNT = 0

class Literal:
    def __init__(self, person, table, isNeg):
        self.person = person
        self.table = table
        self.isNeg = isNeg

    def formattedString(self):
        if (self.isNeg == False):
            return "~X" + str(self.person+1)+ str(self.table+1) + " "
        else:
            return "X" + str(self.person+1) + str(self.table+1) + " "

    def complimentary(self, literalB):
        if (self.person == literalB.person and self.table == literalB.table and self.isNeg != literalB.isNeg):
            return True
        return False

    def getCompliment(self):
        return Literal(self.person, self.table, not self.isNeg)

    def same(self, literalB):
        if (self.person == literalB.person and self.table == literalB.table and self.isNeg == literalB.isNeg):
            return True
        return False

    def __repr__(self):
        return 'X{}{}'.format(self.person+1, self.table+1) if self.isNeg else  '~X{}{}'.format(self.person+1, self.table+1)
        #return '({},{},{})'.format(self.person, self.table, self.isNeg)

    def __hash__(self):
        return hash((self.person, self.table))

    def __eq__(self, other):
        try:
            return (self.person, self.table, self.isNeg) == (other.person, other.table, other.isNeg)
        except AttributeError:
            return NotImplemented

    def applyModel(self, model):
        if (self in model):
            return model[self]
        else:
            return not model[self.getCompliment()]

"""
#Helper functions
"""
def getFormat(ci):
    result = ""
    firstRecord = True
    for _c in ci.clauses:
        if (firstRecord):
            result = result + _c.formattedString()
            firstRecord = False
        else:
            result += ("V " + _c.formattedString())
    return result

def getFormat_2(tempClause):
    result = ""
    firstRecord = True
    for _c in tempClause:
        if (firstRecord):
            result = result + _c.formattedString()
            firstRecord = False
        else:
            result += ("V " + _c.formattedString())
    return result

def findEffectiveClauses(Clauses, clauseA): #clauses remove ClauseA and
    effectiveResult = []
    for item in Clauses:
        if (item.same(clauseA)):
            continue
        else:
            effectiveResult.append(item)
    return effectiveResult

class WalkSatAlgo:
    def __init__(self, _setOfClause):
        self.setOfClause = _setOfClause

    def getSymbols(self, clause): #Input is a list of Clause class
        result = set() #It will be a dictionary of Literal and value

        for _c in clause:
            for literal in _c.clauses:
                if(literal in result or literal.getCompliment() in result):
                    pass
                else:
                    result.add(literal)
        return result

    def assignRandomValues(self, symbols): #symbols is a set of type <Literal> and this returns dict <Literal, Boolean>

        model = dict()
        for sym in symbols:
            model[sym] = random.choice([True, False])

        return model

    def pl_true(self, clauses, model): #clauses = List<Clause>
        result = False

        for _c in clauses.clauses: #these clauses should be ORed together
            result = result or _c.applyModel(model)

        return result

    def resolve(self,  p=0.5, max_flips=10000):
        symbols = self.getSymbols(self.setOfClause.keys()) #symbols is a dict of Literal --> Value
        #print symbols
        model = self.assignRandomValues(symbols)
        #print model

        for i in range(max_flips):
            #print "------------------Starting iteration : ", i + 1, "with model", model
            satisfied, unsatisfied = [], [] #Both of these are List<Clause>
            for _c in self.setOfClause.keys(): #This is List<Clause>
                (satisfied if self.pl_true(_c, model) else unsatisfied).append(_c)
            #print " Satisfied : ", satisfied
            #print " Unsatisfied : ", unsatisfied

            if (len(unsatisfied) == 0):
                #print " Found solution "
                return model
            randomClause = random.choice(unsatisfied)
            if p > random.uniform(0.0, 1.0):
                sym = random.sample(symbols, 1)
                sym = sym[0]
                #print " PROBABILITY WILL DECIDE ", sym
            else:
                #Flip the symbol that maximizes number of sat clauses
                def sat_count(sym): #This function flips a literal and computes unsatfied clauses
                    #print " request for symbol : ", sym
                    temp_sat, temp_unsat = [], []
                    model[sym] = not model[sym]
                    #print " New model = ", model
                    #count = len([clause for clause in self.setOfClause.keys() if self.pl_true(clause, model)])
                    for _c in self.setOfClause.keys(): #This is List<Clause>
                        (temp_sat if self.pl_true(_c, model) else temp_unsat).append(_c)
                    model[sym] = not model[sym]

                    #print " Satisfied : ", temp_sat
                    #print " UnSatisfied : ", temp_unsat

                    count = len(temp_sat)
                    #print " For sym ", sym, " count = ", count
                    return count
                sym = max(symbols, key=sat_count)
                #print "Selected = ", sym
            model[sym] = not model[sym]

        return None

    def searchForTable(self, person, model):

        for (k, v) in model.items(): #model is dictionary of Literal, boolean
            #print "KV = ", k, v
            if (k.person == person and k.isNeg == True and v == True):
                #print " Picking Literal : ", k, " for person : ", person + 1
                return k.table
            elif (k.person == person and k.isNeg == False and v == False):
                #print " Picking Literal (False match): ", k, " for person : ", person + 1
                return k.table
        return None

    def displayFinalResult(self, model, person, table, target):

        def display_Person_Table(personTable):
            for (k,v) in personTable.items():
                target.write(str(k+1) + " " + str(v+1) + "\n")

        personTable = dict()

        for _p in range(0, person):
            personTable[_p] = None

        tables = set([i for i in range(0, table)])
        persons = set([i for i in range(0, person)])

        for _p in range(0, person):
            tbl = self.searchForTable(_p, model)
            if (tbl is not None):
                personTable[_p] = tbl
                tables = tables - set([tbl])
                persons = persons - set([_p])
                #print " Person : ", _p, " has been seated on ", tbl
                #print " Updated tables : ", tables

        if (len(persons) == 0):
            #print " All person seated."
            display_Person_Table(personTable)
        else:
            #print " Handling the case when not all person were assigned a table"
            for _p in range(0, person):
                if (personTable[_p] is None):
                    personTable[_p] = tables[0]
                    tables = tables - set([tables[0]])
            display_Person_Table(personTable)

class Clause:
    def __init__(self, clauses=[]):
       self.clauses=clauses

    def __repr__(self):
        firstRecord = True
        result = ""
        for _c in self.clauses:
            if (firstRecord):
                result += _c.formattedString()
                firstRecord=False
            else:
                result += ("V " + _c.formattedString())
        return result

class PLResolution:
    def __init__(self, _setOfClause):
        self.setOfClause = _setOfClause

    def isSelfCompliment(self, clauses):
        if (clauses[0].complimentary(clauses[1])):
            return True
        return False

    def pl_resolve(self, ci, cj, resolvedClauses): #Takes input as instances of Clause class

        for i in range(0, len(ci.clauses)):
            for j in range(0, len(cj.clauses)):

                clauseA = ci.clauses[i] #Type wise clauseA is a Literal
                clauseB = cj.clauses[j]

                if (clauseA.complimentary(clauseB)):
                    tempClause = []

                    tempA = findEffectiveClauses(copy.copy(ci.clauses), clauseA)
                    tempB = findEffectiveClauses(copy.copy(cj.clauses), clauseB)

                    if (tempA not in tempClause):
                        tempClause += tempA
                    if (tempB not in tempClause):
                        tempClause += tempB

                    #print "Resolved ", str(getFormat(ci)), " & ", str(getFormat(cj)), " => ", str(getFormat_2(tempClause))

                    if (tempClause == [] or len(tempClause) == 0): #Early termination
                        #print " Terminating early "
                        return [], False

                    else:
                        temp_dict = dict()
                        temp_dict[Clause(tempClause)] = sys.maxint

                        if (len(tempClause) == 2 and self.isSelfCompliment(tempClause)):
                            #print " Ignore because it evaluates to True always"
                            pass

                        elif (self.isSubset(temp_dict, resolvedClauses)):
                            pass
                            #print " Already present in resolved clauses"
                        else:
                            #print " Adding is resolvedClauses"
                            global GLOBAL_CLAUSE_COUNT
                            GLOBAL_CLAUSE_COUNT = GLOBAL_CLAUSE_COUNT + 1
                            resolvedClauses[Clause(tempClause)] = GLOBAL_CLAUSE_COUNT

        return resolvedClauses, True #don't add ci and cj in resolvedClauses if nothing is common between them

    def applyResolution(self):
        new = dict()
        while True:
            n = len(self.setOfClause.items())
            pairs = [(self.setOfClause.items()[i][0], self.setOfClause.items()[j][0]) for i in range(n) for j in range(i+1, n)]

            resolvedClauses = dict()
            for (ci, cj) in pairs:
                resolvents, result = self.pl_resolve(ci, cj, resolvedClauses)
                if not( result) :
                    print " PHI FOUND. RETURNING FALSE"
                    return False
                if (len(new.keys()) == 0):
                    new = resolvents
                else:
                    new.update(resolvents)

            print "Looped through all pairs"

            if(self.isSubset(new, self.setOfClause)):
                print " SUBSET FOUND. WE ARE IN LOOP. RETURNING TRUE"
                return True
            else:
                print " Updating set of clause"
                self.setOfClause = self.merge(self.setOfClause, new)
                #print " After Updating set of clause for next iteration "
                displayCNF(self.setOfClause)
                print "==================End Display============="

    def isMatch(self, cA, cB):

        list1 = cA.clauses
        list2 = cB.clauses

        if (len(list1) != len(list2)):
            return False

        difference = set(list1) - set(list2)

        if (len(difference) == 0):
            return True
        return False

    def merge(self, dictionaryOfClause, new):
        resultantDictionary = copy.copy(dictionaryOfClause)

        for _blockNew, _valNew in new.items():
            found = False
            for _blockold, _valold in dictionaryOfClause.items():

                if(self.isMatch(_blockNew, _blockold)):
                    found=True
                    break

            if (found == True):
                continue #Go to next block, #already exists do nothing to resultantDictionary
            else:
                resultantDictionary[_blockNew] = _valNew
        return resultantDictionary

    def isSubset(self, ClauseSetA, ClauseSetKB): #If each item of ClauseSetA is already present in ClauseSetKB

        found = False
        length=len(ClauseSetA.items()) #these many number of blocks should match
        count = 0;

        for _clauseSetA, valA in ClauseSetA.items():

            found = False
            for blockKB, valBR in ClauseSetKB.items():

                if (self.isMatch(_clauseSetA, blockKB)):
                    found=True
                    break
            if (found == True): #Not a subset, More clauses to go to compare
                count = count + 1
                continue
            else:
                return False
        if (found == True and count == length):
            return True
        return False

def displayCNF(setOfClauses):

    for clause, value in sorted(setOfClauses.items(), key=lambda x: x[1]):
        firstRecord = True
        result = ""
        for _c in clause.clauses:
            if (firstRecord):
                result += _c.formattedString()
                firstRecord=False
            else:
                result += ("V " + _c.formattedString())
        print result

def  onePersonOneTable(person, tables):

    global GLOBAL_CLAUSE_COUNT
    GLOBAL_CLAUSE_COUNT = GLOBAL_CLAUSE_COUNT + 1

    for i in range(0, person):
        onePersonAtLeastOneTableClause = list()

        for j in range(0, tables):
            onePersonAtLeastOneTableClause.append(Literal(i, j, True))

        setOfClauses[Clause(onePersonAtLeastOneTableClause)] = GLOBAL_CLAUSE_COUNT

        for j in range(0, tables):
            for k in range(j+1, tables):
                onePersonAtMaxOneTableClause = []

                literal1 = Literal(i, j , False)
                literal2 = Literal(i, k, False)
                onePersonAtMaxOneTableClause.append(literal1)
                onePersonAtMaxOneTableClause.append(literal2)

                setOfClauses[Clause(onePersonAtMaxOneTableClause)] =  GLOBAL_CLAUSE_COUNT

def getRelation(relationships, relation):
    relation = list(filter(lambda x: x[4] == relation, relationships))
    relation_pairs = list()

    for item in relation:
        relation_pairs.append((int(item[0])-1, int(item[2])-1))
    return relation_pairs

def enemiesGenerator(relationships, tables):
    en = getRelation(relationships, 'E')

    global GLOBAL_CLAUSE_COUNT
    for it in en:
        GLOBAL_CLAUSE_COUNT = GLOBAL_CLAUSE_COUNT + 1
        for i in range(0, tables):
            enemyClause = Clause([])

            literal1 = Literal(it[0], i, False)
            literal2 = Literal(it[1], i, False)

            enemyClause.clauses.append(literal1)
            enemyClause.clauses.append(literal2)

            setOfClauses[enemyClause] = GLOBAL_CLAUSE_COUNT

def friendsGenerator(relationships, tables):
    friends = getRelation(relationships, 'F')

    global GLOBAL_CLAUSE_COUNT
    for it in friends:
        GLOBAL_CLAUSE_COUNT = GLOBAL_CLAUSE_COUNT + 1
        for i in range(0, tables):
            friendClause1 = Clause([])
            friendClause2 = Clause([])

            literal1 = Literal(it[0], i, True)
            literal2 = Literal(it[1], i, False)

            friendClause1.clauses.append(literal1)
            friendClause1.clauses.append(literal2)

            literal3 = Literal(it[0], i, False)
            literal4 = Literal(it[1], i, True)

            friendClause2.clauses.append(literal3)
            friendClause2.clauses.append(literal4)

            setOfClauses[friendClause1] = GLOBAL_CLAUSE_COUNT

            #GLOBAL_CLAUSE_COUNT = GLOBAL_CLAUSE_COUNT + 1
            setOfClauses[friendClause2] = GLOBAL_CLAUSE_COUNT

def convertToCNF(relationships, M, N):

    onePersonOneTable(M, N)
    friendsGenerator(relationships, N)
    enemiesGenerator(relationships, N)

if __name__ == "__main__":
    fileName = "input.txt"
    M = N = 0
    count = 0

    relationships = list()

    for line in open(fileName):
        if (count == 0):
            MN = line.strip().split();
            M = int(MN[0])
            N = int(MN[1])
            count = count + 1
        else:
            relationships.append(line.strip())

    convertToCNF(relationships, M, N)

    print " Started with CNF"
    displayCNF(setOfClauses)

    PLResolve = PLResolution(setOfClauses)
    print PLResolve.applyResolution()

    WalkSat = WalkSatAlgo(setOfClauses)
    model = WalkSat.resolve()

    target = open('output.txt', 'w+')

    if (model is None):
        target.write("no")
    else:
        target.write("yes\n")
        WalkSat.displayFinalResult(model, M, N, target)
    target.close()