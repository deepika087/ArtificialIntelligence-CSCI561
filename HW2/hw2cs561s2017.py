__author__ = 'deepika'

import copy
import time
#import random

"""
https://labs.vocareum.com/main/main.php?m=editor&nav=1&asnid=11155&stepid=11156
"""
class CustomPrint:
    def __init__(self, model, person, table):
        self.model = model
        self.person = person #count of person
        self.table = table

    def printModel(self):
        target = open('output.txt', 'w+')

        if (self.model is None or self.model == False or not isinstance(self.model, dict) or len(self.model) == 0):
            target.write("no")
        else:
            def display_Person_Table(personTable):
                for (k,v) in personTable.items():
                    target.write(str(k+1) + " " + str(v+1) + "\n")

            personTable = dict()

            target.write("yes\n")
            for _p in range(0, self.person):
                personTable[_p] = None

            tables = set([i for i in range(0, self.table)])
            persons = set([i for i in range(0, self.person)])

            for _p in range(0, self.person):
                tbl = self.searchForTable(_p)
                if (tbl is not None):
                    personTable[_p] = tbl
                    tables = tables - set([tbl])
                    persons = persons - set([_p])

            if (len(persons) == 0):
                display_Person_Table(personTable)
            else:
                #print " Handling the case when not all person were assigned a table"
                for _p in range(0, self.person):
                    if (personTable[_p] is None):
                        personTable[_p] = tables[0]
                        tables = tables - set([tables[0]])
                display_Person_Table(personTable)
        target.close()

    def searchForTable(self, _person): #Particular person

        for (k, v) in self.model.items(): #model is dictionary of Literal, boolean
            #print "KV = ", k, v
            if (k.person == _person and k.isNeg == True and v == True):
                #print " Picking Literal : ", k, " for person : ", person + 1
                return k.table
            elif (k.person == _person and k.isNeg == False and v == False):
                #print " Picking Literal (False match): ", k, " for person : ", person + 1
                return k.table
        return None

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
        elif (self.getCompliment() in model):
            return not model[self.getCompliment()]
        else:
            return None

    def inspect(self):
        """
        Should work like this
        inspect_literal(P) -> (P, True)
        inspect_literal(~P) -> (P, False)

        if not (self.isNeg): #IsNeg means form is ~A
            return self, True
        return self.getCompliment(), False
        """
        if (self.isNeg):
            return self, True
        return self.getCompliment(), False

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

class DPLL:
    def __init__(self):
        pass

    def getSymbols(self, knowledgeBase):
        result = set() #It will be a dictionary of Literal and value

        for _c in knowledgeBase:
            target = _c.prop_clause()
            target = set(filter(lambda x: x not in result and x.getCompliment() not in result, target))
            result.update(target)
        return result

    def find_unit_symbol(self, clauses, model): # A clause which has just one literal
        for clause in clauses:
            P, value = clause.unit_clause_assign(model)

            if P: #Return symbol that is a literal and its value
                return P, value
        return None, None

    """
        pure_clause is Literal and pure_clause_value is the value of Literal.
    """
    def extend(self, model, pure_clause, pure_clause_value):
        #logging.debug("Old model was : " + str(model))
        new_model = copy.copy(model)
        new_model[pure_clause] = pure_clause_value
        #logging.debug("Updated model is : " + str(new_model))
        return new_model

    """
        Will return a Literal and its Value
    """
    def find_pure_symbol(self, symbols, clauses):

        for sym in symbols:
            found_pos, found_neg = False, False

            for clause in clauses:
                if not found_pos and clause.contains_symbol(sym):
                    found_pos = True
                if not found_neg and clause.contains_symbol(sym.getCompliment()):
                    found_neg = True

            if found_pos != found_neg:
                return sym, found_pos #Could be found ~A or A
        return None, None

    """
        If this code is called if call to pure clause is successful
        then this will be definitely be true becuase this literal will certainly be there
        Its compliment is not possible hence it is okay.
    """
    def removeClause(self, symbols, literal): #symbols is a list of literals
        if (literal in symbols):
            symbols.remove(literal)
        elif(literal.getCompliment() in symbols):
            symbols.remove(literal.getCompliment())
        return symbols

    def dpll_satisfiable(self, cnfKB):
        symbols=self.getSymbols(cnfKB)
        return self.dpll(cnfKB, symbols, {})

    def dpll(self, clauses, symbols, model):
        unknown_clauses = []

        for clause in clauses:
            val=clause.pl_true(model)

            if val is False:
                return False

            if val is not True:
                unknown_clauses.append(clause)

        if not unknown_clauses:
            return model

        pure_clause, pure_clause_value = self.find_pure_symbol(symbols, unknown_clauses)
        if pure_clause is not None:
            return self.dpll(clauses, self.removeClause(symbols, pure_clause), self.extend(model, pure_clause, pure_clause_value))

        unit_clause, unit_clause_value = self.find_unit_symbol(clauses, model)
        if unit_clause is not None:
            return self.dpll(clauses, self.removeClause(symbols, unit_clause), self.extend(model, unit_clause, unit_clause_value))

        if not symbols:
            #exit()
            return False
        symbols = list(symbols)
        P, symbols = symbols[0], set(symbols[1:])
        return (self.dpll(clauses, symbols, self.extend(model, P, True)) or
            self.dpll(clauses, symbols, self.extend(model, P, False)))

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

def getSpecificRelation(relationships, relation):
    filteredList = []

    for _input in relationships:
        _inputTokens = _input.split()

        if (_inputTokens[2] == relation): #Second index will have the actual relationship
            filteredList.append(_input)

    relation_pairs = list()
    for item in filteredList:
        item = item.split()
        relation_pairs.append((int(item[0])-1, int(item[1])-1))
    return relation_pairs

def enemiesGenerator(relationships, tables):
    en = getSpecificRelation(relationships, 'E')

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
    friends = getSpecificRelation(relationships, 'F')

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

def manageWorkFlow():
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
    displayCNF(cnfKB)
    _DPLL = DPLL()

    startTime = time.time()
    model = _DPLL.dpll_satisfiable(cnfKB)
    print " time taken by main DPLL is : ", time.time() - startTime

    _CustomPrint = CustomPrint(model, M, N)
    _CustomPrint.printModel()

if __name__ == "__main__":

    manageWorkFlow()

