HW 2 Details and Work log

The initial assignment was to implement pl_resolution and if it returns true then call WalkSat.

First attempt:
hw2cs561s2017_old - In this I implemented pl_reoslution algorithm to check if the given clauses are satsfiable. But it didn't work for
                    large inputs. For example if relations are huge and they keep multiplying this logic failed. Even though Walksat was working
                    fine with no timeouts and most of the times I was able to find a satisfiable result well on time.

Second attempt :
BackUphw2cs561s2017 - In this file I tried to optimize of pl_resolution.
                    Out of many a few are :
                        1.) If you have clause such as A V A then reduce it to A. Can be found on line 288 in Class PLResolution
                        2.) If you have clause of length greater than 2. Then remove tautologies. Such that is you have expression of the
                        form A V ~A V X V Y V Z and so on then just remove this clause.
                        3.) Re-use the list resolvents. But that didn't help a lot becuase if I used to make fresh resolvent in every
                        loop merging would take time and if I re-used loop then pl_resolve function would take time. So it was of no use.
                        4.) While checking if given dictionary A is a subset of dictionary B. I removed all the matched clause from A
                        which were indeed part of B. becuase just a step later we would merge and then again we would check if
                        it is already present.
                        5.) Use of custom merge function rather than library update function available for dictionary.

Data structures used in attempt1 and attempt2:
Class Literal : <Person, table, isNeg>
Class Clause  : List<Literal> also called clauses
Global dictionary : Called setOfClauses which would have mapping of a Clause instance with a global integer
                    which was again of no use. That integer didnot help anywhere.

Third Attempt :
hw2cs561s2017 - After a lot of msgs to TA they finally relaised the input 3 and 5 can not be done within 2 min.So they allowed us to use
                DPLL algorithm
                Data structure used :
                Class Literal : <Person, table, isNeg>
                Class Clause  : List<Literal> also called literals

                Final clauses were stored in cnfKB local variable which was a List<Clause> rather than dictionary as in previous case.

                WalkSat Algorithm also worked fine but it was commented out becuase DPLL also returns a satisfiable model.

                Class CustomPrint to handle all print related stuff.
This version works for all cases well within time limit

