
from parse import parse_file, Table, Task, Node, parse_seq

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


def contra_check(queries, conditions):
    '''
    check whether queries are contradict to conditions
    '''
    for key in queries.keys():
        if key in conditions.keys():
            if conditions[key] != queries[key]:
                return True
    return False

def parse_to_list(index, length):

    if index > (2**length-1):
        return None
    result, tmp = list(), index
    for i in xrange(length-1, -1, -1):
        flag = tmp >> i
        result.append('+' if flag else '-')
        tmp = tmp - flag* 2**i
    return result


def parse_to_dict(in_list, index):

    length, re_list = len(in_list), list(in_list)
    temp = index
    re_list.reverse()
    if (2**length-1) < index:
        return None
    result = dict()
    for key in re_list:
        result[key] = temp%2
        temp = temp /2
    return result



def answer_p(queries, table):

    if not queries:
        # queries is empty, just return 1
        return 1.0

    # recursion terminating condition
    # the parents of the node in queries are in queries == terminate
    termi = True
    for key in queries.iterkeys():
        for parent_node in table[key].parents:
            if not parent_node in queries.keys():
                termi = False
                break
        if termi == False:
            break
    # things to do when terminating condition holds
    if termi:
        result = 1
        for node_name in queries.iterkeys():
            if table[node_name].decision:
            # jump to next loop if this node is a decision node
                continue
            index = 0
            for parent_name in table[node_name].parents:
                index = (index<<1) + queries[parent_name]
            result *= table[node_name].prob_table[index] if queries[node_name] else (1 - table[node_name].prob_table[index])
            #print " Index = ", index
            #print " Result before exiting recursion for node : ", node_name, " is ", result
        return result

    # things to do when terminating condition doesn't hold
    for node_name in queries.iterkeys():
        index = 0
        for parent_name in table[node_name].parents:
            if not parent_name in queries.keys():
                new_queries0 = dict(queries)
                new_queries0.update(**{parent_name:0})
                new_queries1 = dict(queries)
                new_queries1.update(**{parent_name:1})
                result = answer_p(new_queries0, table) + answer_p(new_queries1, table)
                #print " Result after recursion for node : ", node_name, " is ", result
    return result


def ask_p(queries, conditions, table):
    '''
    queries and conditions are dict with node_name and node value
    calculate the conditional probability
    '''
    if contra_check(queries, conditions):
        return 0.0
    new_queries = dict(queries)
    new_queries.update(**conditions)
    prob0 = answer_p(new_queries, table)
    prob1 = answer_p(conditions, table)

    print " Prob0 : ", prob0, " prob1 : ", prob1
    return prob0/prob1

def ask_eu(queries, conditions, utility, table):
    '''
    return the expected utility
    '''
    eu = 0
    # new_queries = dict(queries)
    for i in xrange(2**len(utility.parents)):
        new_query = parse_to_dict(utility.parents, i)
        # if the condition in new_condition is contradict to the condition in new_queries
        # jump to next loop
        # if contra_check(new_queries, new_condition):
        #	continue
        # two conditions are consistent with each other
        new_condition = dict(queries)
        new_condition.update(**conditions)
        eu += utility.prob_table[i]*ask_p(new_query, new_condition, table)
    return eu

def ask_meu(queries, conditions, utility, table):
    '''
    '''
    meu = (-100000.0, 0)
    for i in xrange(2**len(queries)):
        new_queries = parse_to_dict(queries, i)
        this_eu = ask_eu(new_queries, conditions, utility, table)
        if this_eu > meu[0]:
            meu = (this_eu, i)
    print " MeU[i] : ", meu[1]
    result = parse_to_list(meu[1], len(queries))
    return ' '.join(result), meu[0]


if __name__ == '__main__':
    import doctest, decimal
    doctest.testmod()
    filename = 'input.txt'
    tasks,table,utility = parse_file(filename)
    print tasks
    print table
    print utility
    for task in tasks:
        if task.type == 'P':
            result = ask_p(task.query, task.condition, table)
            print my_round(result, 2)
        elif task.type == 'EU':
            print ask_eu(task.query, task.condition, utility, table)
        elif task.type == 'MEU':
            result = ask_meu(task.query, task.condition, utility, table)
            print result[0], result[1]
