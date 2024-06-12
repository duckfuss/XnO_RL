# aim is to use reinforcement learning to perfect noughts and crosses
import random, time, os, pickle

'''
Functional!
'''

#----------classes----------#
class GameBoard:
    def __init__(self) -> None:
        self.gameSize = 4
        self.board = self.createBoard(size=self.gameSize)
        self.inARow = 4 # num in a row required for a win
        self.pieceDict = {0:"❌", 1:"⭕"} # map  values of 0 and 1 to X/O symbol
    def reset(self):
        self.board = self.createBoard(size=self.gameSize)
    def createBoard(self, size=3):
        tempBoard = []
        for row in range(size):
            tempBoard.append([])
            for col in range(size):
                tempBoard[row].append("  ")
        return tuplify(tempBoard)
    def fancyPrint(self) -> None:
        # print top col coordinates
        printLine = "  " # correct padding
        for col in range(self.gameSize):
            printLine = printLine + str(col) + "   "
        print(printLine)
        # print gameboard and side coordinates
        for row in range(self.gameSize):
            printLine = str(row)
            # print horizontal stripe with inputs
            for col in range(self.gameSize):
                printLine += " " + self.board[row][col]
                if col +1 != self.gameSize:
                    printLine += "┃"
            print(printLine)
            # print horizontal stripe without inputs
            printLine = " ━"
            if row+1 != self.gameSize:
                for char in range(self.gameSize-1):
                        printLine += "━━╋━"
                print(printLine+"━━")
    def placePiece(self, row, col, piece = "?"):
        tempBoard = listify(self.board)
        if tempBoard[row][col] == "  ":
            tempBoard[row][col] = self.pieceDict[piece]
            self.board = tuplify(tempBoard)
            return [True, tuplify(tempBoard)]
        else:
            return [False]
    
class RL_Computer():
    def __init__(self, piece) -> None:
        self.FSaver = FileSaver(str(piece))
        self.memoryDict = self.FSaver.load()
        print("mem dict created")
        # for input states: (board-state):[list of explored future Ouptut-states]
        # for output states: (board-state):score
        self.gameList = []
        self.piece = piece

    def selectBestMove(self, board, bestMove=False, debug=False):
        # selects the best possible next move given a current board state
        possibleStates = []
        possibleScores = []
        for pState in self.memoryDict[board]:
            possibleScores.append(self.memoryDict[pState])
            possibleStates.append(pState)
        if debug: print(possibleScores, "\n", possibleStates)
        # take weighted random choice
        if not bestMove:
            possibleScores.append(0)
            possibleStates.append('RANDOM')
            offset = min(possibleScores)
            posWeights = [z - offset + 1 for z in possibleScores] # make weights +ve
            nextState = random.choices(possibleStates, posWeights)[0]
        if bestMove:
            nextState = possibleStates[possibleScores.index(max(possibleScores))]
        if debug: print("\n", nextState)
        return nextState
    
    def updateBoard(self, board, nextState):
        # finds & updates coord given a current boardstate and a desired state
        for row in range(len(nextState)):
            for col in range(len(nextState)):
                if board[row][col] != nextState[row][col]:
                    boardUpdate = XnO.placePiece(row, col, piece=self.piece)
                    return boardUpdate
    
    def pickValidRandom(self, board):
        boardUpdate = [False] # loops if random turn is impossible move
        while not boardUpdate[0]:
            # picks a random coordinate
            row = random.randrange(len(board))
            col = random.randrange(len(board))
            boardUpdate = XnO.placePiece(row, col, piece=self.piece)
        return boardUpdate

    def updateMemDict(self, board, boardUpdate):
        # adds the board in mem.dict if not already present
        if board not in self.memoryDict: # create new board in memory dict
            self.memoryDict[board] = [boardUpdate[1]]
        # if current state is present, but the next move isn't in current state's list,...
        # ...append the next move to the current states' list of options
        elif boardUpdate[1] not in self.memoryDict[board]: # append to existing board
            self.memoryDict[board].append(boardUpdate[1])
        # if next state is new, create an entry in memDict for the next move with score of 0
        if boardUpdate[1] not in self.memoryDict:
            self.memoryDict[boardUpdate[1]] = 0

    def computerTurn(self, board, bestMove=False, debug=False):
        nextState = []
        # if computer knows next best move
        if board in self.memoryDict:
            nextState = self.selectBestMove(board, bestMove, debug)
            if nextState != 'RANDOM':
                boardUpdate = self.updateBoard(board, nextState)
                
        # if computer doesn't know best move
        if board not in self.memoryDict or nextState == 'RANDOM':
            # picks a valid random position
            boardUpdate = self.pickValidRandom(board)
            # updates memoryDict
            self.updateMemDict(board, boardUpdate)
        self.gameList.append(boardUpdate[1])

    def debrief(self, isWin):
        numMoves = len(self.gameList)
        for i in range(numMoves):
            state = self.gameList[i]
            # calculate new score
            if isWin:
                self.memoryDict[state] += 0.25*(i**2)
            else:
                self.memoryDict[state] -= (i**2)
        self.gameList = []

class FileSaver():
    def __init__(self, name) -> None:
        self.fileName = os.path.join(os.path.dirname(__file__), name + ".txt")
    def load(self):
        if os.path.exists(self.fileName):
            print("loading file")
            dictFile = open(self.fileName, "rb")
            contents = pickle.load(dictFile)
            dictFile.close()
            print("file loaded", len(contents))
            return contents
        else:           
            return {}
    def save(self, toWriteDict):
        dictFile = open(self.fileName, "wb")
        pickle.dump(toWriteDict, dictFile)
        dictFile.close()

#----------functions----------#
def playerTurn(turns):
    while True: # loop if invalid inputs are given
        col = int(input("what column do you want to place your piece in? "))
        row = int(input("what row do you want to place your piece in? "))
        if XnO.placePiece(row, col, piece=turns%2)[0]:
            break

def check(gameBoard, inARow, startPos, stepInc, boundaryInc):
    # stepInc = [row,col] - direction to move active square each step
    # boundaryInc = [row,col] - direction to increment the new start position when on boundary
    activeSquare = startPos.copy()
    checkList = []
    while True:
        # update checkList
        checkList.append(gameBoard[activeSquare[0]][activeSquare[1]])
        if len(checkList) > inARow:
            checkList.pop(0)
        # check for nInARow
        result = checkList.count(checkList[0])
        if result == inARow and checkList[0] != '  ':
            return [True, checkList[0]]
        # increment the active square by adding stepInc to activeSquare
        activeSquare = [sum(x) for x in zip(activeSquare, stepInc)]
        # check for out of bounds, and correct accordingly
        if activeSquare[0] == len(gameBoard) or activeSquare[1] == len(gameBoard) or activeSquare[0] < 0 or activeSquare[1] < 0:
            startPos = [sum(x) for x in zip(startPos, boundaryInc)] # set new start position
            activeSquare = startPos.copy() # set activeSquare to start position
            checkList = [] # clear checklist
        if startPos[0] < 0 or startPos[0] == len(gameBoard) or startPos[1] < 0 or startPos[1] == len(gameBoard):
            return [False]

def checkDraw(gameBoard):
    for row in gameBoard:
        if "  " in row:
            return False
    return True

def checkInARow():
    # check diagonals
    checkTLBR1 = check(XnO.board, XnO.inARow, [len(XnO.board)-1,0], [1,1], [-1,0])
    checkTLBR2 = check(XnO.board, XnO.inARow, [0,len(XnO.board)-1], [1,1], [0,-1])
    checkTRBL1 = check(XnO.board, XnO.inARow, [0,0], [-1,-1], [0,1])
    checkTRBL2 = check(XnO.board, XnO.inARow, [len(XnO.board)-1,len(XnO.board)-1], [-1,-1], [-1,0])
    # check orthoganals
    checkRows = check(XnO.board, XnO.inARow, [0,0], [0,1], [1,0])
    checkCols = check(XnO.board, XnO.inARow, [0,0], [1,0], [0,1])
    checkList = [checkTLBR1[0], checkTLBR2[0],
                checkTRBL1[0], checkTRBL2[0], 
                checkRows[0], checkCols[0]]
    if True in checkList:
        return True
    else:
        return False


def resetValues():
    global draw, turns, gameDone
    XnO.reset()
    comp0.gameList, comp1.gameList = [], []
    draw = False
    turns = 0
    gameDone = False

#----------helper funcs----------#
def listify(t):
    return list(list(i) for i in t)
def tuplify(l):
    return tuple(tuple(i) for i in l)

#----------initialisation----------#
XnO = GameBoard()
comp0 = RL_Computer(0) # X
comp1 = RL_Computer(1) # O

#----------variables----------#
turns = 0
draw = False
leng = 0

#----------main code----------#

def trainAi(lim):
    global turns, draw, gameDone
    gameDone = False
    gameLimit, games = lim, 0
    leng = 0
    print("commencing training")
    while games < gameLimit:
        games += 1
        while not gameDone:
            turns += 1
            # play computer's turn
            if turns % 2 == 0:
                comp0.computerTurn(XnO.board)
                if leng != len(comp0.memoryDict) and games % 10000 == 0:
                    leng = len(comp0.memoryDict)
                    print("states explored:", leng, "│  games played:", games)
            else:
                comp1.computerTurn(XnO.board)
            # check for in a row and draws
            if checkDraw(XnO.board):
                draw = True
                gameDone = True
            elif checkInARow():
                gameDone = True
        # Learn based on win/loose
        if turns % 2 == 0 and not draw:
            comp0.debrief(True)
            comp1.debrief(False)
        elif not draw:
            comp1.debrief(True)
            comp0.debrief(False)
        # reset
        resetValues()
    print("saving values")
    comp0.FSaver.save(comp0.memoryDict)
    comp1.FSaver.save(comp1.memoryDict)
    print("values saved")

def playAi():
    global turns, draw, gameDone
    resetValues()
    gameDone = False
    while not gameDone:
        turns += 1
        # play turns:
        if turns%2 ==0:
            comp0.computerTurn(XnO.board, bestMove=True, debug=True)
        else:
            XnO.fancyPrint()
            playerTurn(turns)

        # Check for draw or in a row
        if checkDraw(XnO.board):
            draw = True
            break
        elif checkInARow():
            break

    if turns % 2 == 0 and not draw:
        print("COMPUTER WINS")
    elif not draw:
        print("YOU WIN")


trainAi(100)
while True:
   playAi()
