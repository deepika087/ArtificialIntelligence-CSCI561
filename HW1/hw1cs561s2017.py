#!/usr/bin/python
"""
Assumption is that code will stop only when there are two consecutive pass not when the opponent has no chance to play
"""
import sys
from scipy.constants.codata import value

NAMES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
POSITION_WEIGHTS = (( 99, -8, 8, 6, 6, 8, -8, 99 ),
                ( -8, -24, -4, -3, -3, -4, -24, -8 ),
                ( 8, -4, 7, 4, 4, 7, -4, 8 ),
                ( 6, -3, 4, 0, 0, 4, -3, 6 ),
                ( 6, -3, 4, 0, 0, 4, -3, 6 ),
                ( 8, -4, 7, 4, 4, 7, -4, 8 ),
                ( -8, -24, -4, -3, -3, -4, -24, -8 ),
                ( 99, -8, 8, 6, 6, 8, -8, 99 ))
class Agent:

    player = ''
    matrix = ''
    cutOffDepth = 0
    opponent = ''

    def __init__(self, player, cutoffDepth, matrix):
        """
        self.player = player
        self.matrix = matrix
        self.cutoffDepth = cutoffDepth
        self.opponent = 'X' if player == 'O' else 'O'
        """
        Agent.player = player
        Agent.matrix = matrix
        Agent.cutOffDepth = cutoffDepth
        Agent.opponent = 'X' if player == 'O' else 'O'


    @staticmethod
    def getEvaluation(matrixM):
        _p = Agent.player
        _o = Agent.opponent

        sum = 0
        for i in range(8):
            for j in range(8):
                if (matrixM[i][j] == _p):
                    sum = sum + POSITION_WEIGHTS[i][j]
                if (matrixM[i][j] == _o):
                    sum = sum - POSITION_WEIGHTS[i][j]
        return sum

    @staticmethod
    def isGameOver(startState):
        xCount = 0
        oCount = 0
        sCount = 0

        for i in range(8):
            for j in range(8):
                if (startState.matrix[i][j] == Agent.player):
                    xCount = xCount + 1
                elif(startState.matrix[i][j] == Agent.opponent):
                    oCount = oCount + 1
                else:
                    sCount = sCount + 1

        if(xCount == 0 or oCount == 0 or sCount == 0):
            return True;
        else:
            return False;


class AlphaBeta:

    def __init__(self, matrix, player, opponent, cutoffDepth):
        self.opponent = opponent
        self.player = player
        self.cutoffDepth = cutoffDepth
        self.matrix = matrix
        self.path = list()

    def printLogFiles(self):
        alpha = -sys.maxint
        beta = sys.maxint
        root = BoardState("root", 0, self.matrix, self.player)
        root.parent = root
        root.nextBoardState = root
        self.maxValue(root, alpha, beta)
        return root.nextBoardState.printGrid(), self.path

    def maxValue(self, boardState, alpha, beta):
        children = self.findStates(boardState)
        opponentState = BoardState("pass", boardState.depth + 1, boardState.matrix, boardState.opponent)
        childrenOfOpponent = self.findStates(opponentState)

        #Agent.isGameOver(boardState) or
        if (boardState.depth == self.cutoffDepth or boardState.node == "pass" and boardState.parent.node == "pass"):
            valueObtained = Agent.getEvaluation(boardState.matrix)
            boardState.valueObtained = valueObtained
            self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta))
            return valueObtained

        boardState.valueObtained = -sys.maxint
        self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta));
        if (len(children) == 0 and len(childrenOfOpponent) > 0):
            opponentState.parent = boardState
            children.append(opponentState)

        if (len(children) == 0 and len(childrenOfOpponent) == 0):
            opponentState.parent = boardState
            children.append(opponentState)

        for child in children:
            boardState.valueObtained = max(boardState.valueObtained, self.minValue(child, alpha, beta))

            child.parent = boardState

            if (boardState.valueObtained >= beta):
                self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta))
                return boardState.valueObtained
            else:
                if (boardState.valueObtained > alpha):
                    boardState.nextBoardState = child
                alpha = max(alpha, boardState.valueObtained)
            self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta));
        return boardState.valueObtained

    def minValue(self, boardState, alpha, beta):
        children = self.findStates(boardState)
        opponentState = BoardState("pass", boardState.depth + 1, boardState.matrix, boardState.opponent)
        childrenOfOpponent = self.findStates(opponentState)

        #Agent.isGameOver(boardState) or
        if (boardState.depth == self.cutoffDepth or boardState.node == "pass" and boardState.parent.node == "pass"):
            valueObtained = Agent.getEvaluation(boardState.matrix)
            boardState.valueObtained = valueObtained
            self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta))
            return valueObtained

        boardState.valueObtained = sys.maxint
        self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta));

        if (len(children) == 0 and len(childrenOfOpponent) > 0):
            opponentState.parent = boardState
            children.append(opponentState)

        if (len(children) == 0 and len(childrenOfOpponent) == 0):
            opponentState.parent = boardState
            children.append(opponentState)

        for child in children:
            boardState.valueObtained = min(boardState.valueObtained, self.maxValue(child, alpha, beta))
            child.parent = boardState

            if (boardState.valueObtained <= alpha):
                self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta))
                return boardState.valueObtained
            else:
                if (boardState.valueObtained < beta):
                    boardState.nextBoardState = child
                beta = min(beta, boardState.valueObtained)
            self.path.append(self.printCustom(boardState.node, boardState.depth, boardState.valueObtained, alpha, beta))
        return boardState.valueObtained

    def findStates(self, startState):
        boardStates = list()
        for i in range(8):
            for j in range(8):
                flipPositions = self.getFlipPositions(startState, i, j)
                if (len(flipPositions) > 0):
                    flipPositions.append((i, j))
                    flippedBoard = self.getFlippedBoard(startState, flipPositions)
                    #print "flippedBoard = ", flippedBoard
                    updatedBoard = BoardState(NAMES[j] + str(i + 1), startState.depth + 1, flippedBoard, startState.opponent)
                    boardStates.append(updatedBoard)
        return boardStates

    def printCustom(self, node, depth, value, alpha, beta):
        temp_str = ''
        temp_str += node
        temp_str += ","
        temp_str += str(depth)
        temp_str += ","
        temp_str += str(self.isInfinity(value))
        temp_str += ","
        temp_str += self.isInfinity(alpha)
        temp_str += ","
        temp_str += self.isInfinity(beta)
        return temp_str

    def isInfinity(self, val):
        if (val == sys.maxint):
            return "Infinity"
        elif (val == -sys.maxint):
            return "-Infinity"
        else:
            return str(val)

    def makeSureBounds(self, i, j):
        if (i < 0):
            return False
        if (i >= 8):
            return False
        if(j < 0):
            return False
        if(j >= 8):
            return False
        return True

    def getFlipPositions(self, startState, i, j):
        flipPositions=list()

        if (self.makeSureBounds(i, j) and startState.matrix[i][j] == '*'):
            for dx in range(-1, 2, 1):
                for dy in range(-1, 2, 1):
                    if (dx == 0 and dy == 0):
                        continue
                    tx = i + dx
                    ty = j + dy
                    while(self.makeSureBounds(tx, ty) and startState.matrix[tx][ty] != '*'):
                        if (ord(startState.matrix[tx][ty]) != ord(startState.player)):
                            tx = tx + dx
                            ty = ty + dy
                        else:
                            #print "For tx = " , tx , " and ty = " , ty
                            px = tx - dx
                            py = ty - dy
                            while( not (px ==i and py == j)):
                                flipPositions.append((px, py))
                                px = px - dx
                                py = py - dy
                            break
        return flipPositions


    def getFlippedBoard(self, startState, flipPositions):
        matrix2 = list()
        for line in startState.matrix:
            matrix2.append(line)

        for pos in flipPositions:
            #print "Marking position: ", pos[0], ", ", pos[1]
            #print "Value to be replaced : ", matrix2[pos[0]][pos[1]]
            route = matrix2[pos[0]]
            route = list(route)
            route[pos[1]] = startState.player
            matrix2[pos[0]] = ''.join(route)
        return matrix2

class BoardState:

        def __init__(self, node, depth, matrix, player):
            self.node = node
            self.depth = depth
            self.matrix = matrix
            self.player = player
            self.opponent = 'X' if self.player == 'O' else 'O'
            self.parent = ''
            self.nextBoardState= ''
            self.alpha = 0
            self.beta = 0
            self.valueObtained = 0

        def __str__(self):
            return '[Node = ", self.node, " Depth = ", self.depth, " matrix = ", self.matrix, "player = ", self.player, "]'

        def __repr__(self):
            return self.__str__()

        def printGrid(self):
            lineOfGrid = ""
            for i in range(8):
                lineOfGrid += self.matrix[i] + "\n"
            return lineOfGrid

if __name__ == "__main__":
    if (len(sys.argv) >= 3):
        fileName = sys.argv[2]
    else:
        fileName = "input.txt"

    count = 0
    cutOffDepth = -1
    player = ''
    matrixLines = list()
    for line in open(fileName):
        if (count == 0):
            player = chr(ord(line[0]))
            count = count + 1
        elif (count == 1):
            cutOffDepth = int(line[0])
            count = count + 1
        else:
            matrixLines.append(line.strip())

    agent = Agent(player, cutOffDepth, matrixLines)
    #print "Player = ",  agent.player
    #print "Opponent = ", agent.opponent
    #print "Cuttoff Depth = ", agent.cutOffDepth
    #print "Input = ", agent.matrix

    alphaBeta = AlphaBeta(agent.matrix, agent.player, agent.opponent, agent.cutOffDepth)
    gridResult, path = alphaBeta.printLogFiles()
    target = open('output.txt', 'w+')
    #print "file created successfully"

    for _ in gridResult:
        target.write(_)
    target.write("Node,Depth,Value,Alpha,Beta\n")
    for _ in path:
        target.write(_ + "\n")
    target.close()

