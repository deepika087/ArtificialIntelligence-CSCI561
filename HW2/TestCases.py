#!/usr/bin/python

__author__ = 'deepika'

import logging
import random
#from os import system
import copy
"""
https://labs.vocareum.com/main/main.php?m=editor&nav=1&asnid=11155&stepid=11156
"""

import hw2cs561s2017 as workflow

logging.basicConfig(filename='seating_arrangement_testing.log',level=logging.DEBUG)

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
        if (len(model) == 0):
            return None

        result = False

        for literal in self.literals: #these clauses should be ORed together
            temp_result = literal.applyModel(model)
            if (temp_result is None):
                return None
            result = result or temp_result

        return result

    def is_unit(self):
        return True if len(self.literals) == 1 else False

    def contains_symbol(self, symbol): #symbols is Literal here
        if (symbol in self.literals):
            return True
        return False

    def unit_clause_assign(self, model):
        P, value = None, None

        for literal in self.literals:
            sym, positive = literal.inspect() #This will return a literal and its value
            if sym in model:
                if model[sym] == positive:
                    return None, None
            elif P:
                return None, None
            else:
                P, value = sym, positive
        return P, value

class Literal:
    def __init__(self, person, table, isNeg):
        self.person = person
        self.table = table
        self.isNeg = isNeg

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

    def formattedString(self):
        if (self.isNeg == False):
            return "~X" + str(self.person+1)+ str(self.table+1) + " "
        else:
            return "X" + str(self.person+1) + str(self.table+1) + " "

class Relation:
    def __init__(self, person1, person2, rel):
        self.person1 = person1
        self.person2 = person2
        self.rel = rel

    def getCompliment(self):
        return Relation(self.person1, self.person2, 'E' if self.rel == 'F' else 'F')

    def __repr__(self):
        return '{} {} {}'.format(self.person1, self.person2, self.rel)

    def __str__(self):
        return '{} {} {}'.format(self.person1, self.person2, self.rel)

    def __hash__(self):
        return hash((self.person1, self.person2))

    def __eq__(self, other):
        try:
            return isinstance(other, self.__class__) and (self.person1, self.person2, self.rel) == (other.person1, other.person2, other.rel)
        except AttributeError:
            return NotImplemented

def createInputFile(persons, tables, relationships):
    target = open('input.txt', 'w+')
    target.write(str(persons) + " " + str(tables) + "\n")
    for relation in relationships:
        target.write('{} {} {}\n'.format(relation.person1, relation.person2, relation.rel))
    target.close()

def createLiteralFromOutputFile():

    sitting = dict()
    for line in open('output.txt', 'r'):
        line = line.strip()
        if (line == "no"):
            return sitting
        elif(line.strip() == "yes"):
            continue
        elif(len(line) == 0):
            break
        else:
            line = line.split()
            sitting[int(line[0])] = int(line[1])
    return sitting

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

def getRelation(relationships, _relation): #relationships : List<Relation>
    logging.debug("Relationships : " + str(relationships) + " and relation : " + str(_relation))
    _relation = list(filter(lambda x: x.rel == _relation, relationships))
    relation_pairs = list()

    for item in relationships:
        #print _rel, " ", type(_rel)
        relation_pairs.append((int(item.person1)-1, int(item.person2)-1))
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

"""
relationships : List<Relation> : Input given
literals : List<Literal> : output from actual homework assignment
"""
def conditionsMet(relationships, sitting):
    for _rel in relationships:
        if (_rel.rel == 'F'):
            assert sitting[int(_rel.person1)] ==  sitting[int(_rel.person2)]
        else:
            assert sitting[int(_rel.person1)] !=  sitting[int(_rel.person2)]

    return True

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

    testCases = 7 #random.randint(1, 5)
    logging.debug("Will run for {} testcases".format(testCases))

    for _ in range(testCases):
        persons = random.randint(1, 10)
        tables = random.randint(1, 10)
        if (persons - 1 == 1):
            logging.debug("Oops missed one")
            continue
        NumOfRelations = random.randint(1, persons-1) #idealy max relations can be pC2 but I am limiting it to half
        #-1 because say 2 people. only one relationship is possible. No point trying to form 2 relations cz 1 and 2 will be F/E

        logging.debug("Number of persons, tables and relations are {}, {}, {}".format(persons, tables, NumOfRelations))

        i = 0
        relationships = [] #List of Relation
        while (i < NumOfRelations):
            _a = random.randint(1, persons)
            _b = random.randint(1, persons) #To maintain ascending order of a relation.
            if (_a == _b):
                logging.debug("Pass.picked same persons" )
                continue
            _c = random.choice(['E', 'F'])

            relation = Relation(_a, _b, _c)
            twistedRelation = Relation(_b, _a, _c)

            if (relation in relationships or relation.getCompliment() in relationships):
                logging.debug("Pass.Didn't like the relation" + str(relation))
                continue
            elif (twistedRelation in relationships or twistedRelation.getCompliment() in relationships):
                logging.debug("Pass.Didn't like the relation" + str(twistedRelation))
                continue
            else:
                relationships.append(relation) #List<Relation>
                i = i + 1

        createInputFile(persons, tables, relationships)
        logging.debug("Relationships : " + str(relationships))
        logging.debug(".........Calling the hw file..............")
        workflow.manageWorkFlow()
        logging.debug(".........Ending call to the hw file..............")

        #Compare output here
        sitting = createLiteralFromOutputFile()
        logging.debug("Fresh out of oven literals : " + str(sitting))
        if (len(sitting) == 0):
            logging.debug("RESULT: No satisfiable result found")
        else:
            logging.debug("The list of literal is {}".format(str(sitting)))
            logging.debug(" Result recieved : " + str(conditionsMet(relationships, sitting))) #Read input.txt and form CNF form
        logging.debug("=============================================================================")

