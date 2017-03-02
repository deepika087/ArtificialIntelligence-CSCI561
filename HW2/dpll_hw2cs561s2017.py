__author__ = 'deepika'

import copy
import sys
import random
import logging

logging.basicConfig(filename='dpll_debug.log',level=logging.DEBUG)

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
            return isinstance(other, self.__class__) and (self.person, self.table, self.isNeg) == (other.person, other.table, other.isNeg)
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

class WalkSatAlgo:
    def __init__(self, cnfKB):
        self.knowledgeBase = cnfKB #knowledgeBase is a List<Clause>

    #start here
    def getSymbols(self):
        result = set() #It will be a dictionary of Literal and value

        for _c in self.knowledgeBase:
            target = _c.prop_clause()
            target = set(filter(lambda x: x not in result and x.getCompliment() not in result, target))
            result.update(target)
        return result

    def assignRandomValues(self, symbols): #symbols is a set of type <Literal> and this returns dict <Literal, Boolean>

        model = dict()
        for sym in symbols:
            model[sym] = random.choice([True, False])

        return model

    """
    Inputs : clause : Instance of class Clause = List<Literal>
    """
    def resolve(self,  p=0.5, max_flips=10000):
        symbols = self.getSymbols() #Gets symbols from KnowledgeBase which is a List<Clause>
        logging.debug("Set of symbols : " + str(symbols))
        model = self.assignRandomValues(symbols)
        logging.debug("Initial model : " + str(model))

        for i in range(max_flips):
            logging.debug("------------------Starting iteration : " + str(i + 1) + "with model" + str(model))
            satisfied, unsatisfied = [], [] #Both of these are List<Clause>
            for clause in self.knowledgeBase: #This is List<Clause>
                (satisfied if clause.pl_true(model) else unsatisfied).append(clause)
            #print " Satisfied : ", satisfied
            #print " Unsatisfied : ", unsatisfied

            if (len(unsatisfied) == 0):
                print " Found solution "
                return model
            randomClause = random.choice(unsatisfied)
            if p > random.uniform(0.0, 1.0):
                sym = random.sample(randomClause.prop_clause(), 1) #this returns a list. Therefore pick first element to be the effective symbol
                sym = sym[0]
                sym = sym if sym in model else sym.getCompliment()
                logging.debug(" PROBABILITY WILL DECIDE " + str(sym))
            else:
                #Flip the symbol that maximizes number of sat clauses
                def sat_count(sym): #This function flips a literal and computes unsatfied clauses
                    #print " request for symbol : ", sym
                    temp_sat, temp_unsat = [], []
                    model[sym] = not model[sym]
                    #print " New model = ", model
                    #count = len([clause for clause in self.setOfClause.keys() if self.pl_true(clause, model)])
                    for clause in self.knowledgeBase: #This is List<Clause>
                        (temp_sat if clause.pl_true(model) else temp_unsat).append(clause)
                    model[sym] = not model[sym]

                    #print " Satisfied : ", temp_sat
                    #print " UnSatisfied : ", temp_unsat

                    count = len(temp_sat)
                    #print " For sym ", sym, " count = ", count
                    return count
                sym = max(symbols, key=sat_count)
                logging.debug("Selected symbol = " + str(sym))
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
    def __init__(self, literals=[]):
       self.literals=literals

    def __repr__(self):
        firstRecord = True
        result = ""
        for _c in self.literals:
            if (firstRecord):
                result += _c.formattedString()
                firstRecord=False
            else:
                result += ("V " + _c.formattedString())
        return result

    def prop_clause(self): #This will function will receive a Clause as input and it will return symbols in that Clause

        result = set()

        for literal in self.literals:
            if(literal in result or literal.getCompliment() in result):
                pass
            else:
                result.add(literal)

        return result

    def pl_true(self, model): #clauses = List<Clause>
        result = False

        for literal in self.literals: #these clauses should be ORed together
            result = result or literal.applyModel(model)

        return result

class DPLL:
    def __init__(self, cnfKB):
        self.knowledgeBase = cnfKB

def onePersonOneTable(person, tables):

    result = [] #list<Clause>
    for i in range(0, person):
        onePersonAtLeastOneTableClause = list()

        for j in range(0, tables):
            onePersonAtLeastOneTableClause.append(Literal(i, j, True))

        result.append(Clause(onePersonAtLeastOneTableClause))

        for j in range(0, tables):
            for k in range(j+1, tables):
                onePersonAtMaxOneTableClause = []

                literal1 = Literal(i, j , False)
                literal2 = Literal(i, k, False)
                onePersonAtMaxOneTableClause.append(literal1)
                onePersonAtMaxOneTableClause.append(literal2)

                result.append(Clause(onePersonAtMaxOneTableClause))
    return result

def getRelation(relationships, relation):
    relation = list(filter(lambda x: x[4] == relation, relationships))
    relation_pairs = list()

    for item in relation:
        relation_pairs.append((int(item[0])-1, int(item[2])-1))
    return relation_pairs

def enemiesGenerator(relationships, tables):
    en = getRelation(relationships, 'E')

    result = []
    for it in en:
        for i in range(0, tables):
            enemyClause = Clause([])

            literal1 = Literal(it[0], i, False)
            literal2 = Literal(it[1], i, False)

            enemyClause.literals.append(literal1)
            enemyClause.literals.append(literal2)

            result.append(enemyClause)
    return result

def friendsGenerator(relationships, tables):
    friends = getRelation(relationships, 'F')

    result = []
    for it in friends:
        for i in range(0, tables):
            friendClause1 = Clause([])
            friendClause2 = Clause([])

            literal1 = Literal(it[0], i, True)
            literal2 = Literal(it[1], i, False)

            friendClause1.literals.append(literal1)
            friendClause1.literals.append(literal2)

            literal3 = Literal(it[0], i, False)
            literal4 = Literal(it[1], i, True)

            friendClause2.literals.append(literal3)
            friendClause2.literals.append(literal4)

            result.append(friendClause1)

            #GLOBAL_CLAUSE_COUNT = GLOBAL_CLAUSE_COUNT + 1
            result.append(friendClause2)
    return result

def convertToCNF(relationships, M, N):

    cnfKB = [] #List<Clause>
    result = onePersonOneTable(M, N)
    cnfKB += result
    result = friendsGenerator(relationships, N)
    cnfKB += result
    result = enemiesGenerator(relationships, N)
    cnfKB += result

    return cnfKB

def displayCNF(clauses):

    for clause in clauses:
        firstRecord = True
        result = ""
        for _c in clause.literals:
            if (firstRecord):
                result += _c.formattedString()
                firstRecord=False
            else:
                result += ("V " + _c.formattedString())
        print result

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
            line = line.strip()
            if (len(line) == 0):
                break
            else:
                relationships.append(line.strip())

    cnfKB = convertToCNF(relationships, M, N) #List<Clause>

    print " Started with CNF"
    displayCNF(cnfKB)

    DPLL = DPLL(cnfKB)
    WalkSat = WalkSatAlgo(cnfKB)
    model = WalkSat.resolve()

    print " Result found : ", model
    target = open('output.txt', 'w+')

    if (model is None):
        target.write("no")
    else:
        target.write("yes\n")
        WalkSat.displayFinalResult(model, M, N, target)
    target.close()