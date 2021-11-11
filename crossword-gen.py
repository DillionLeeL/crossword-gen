import random
import re
import string
from copy import deepcopy
import time
start_time = time.time()

class Coord(object):
    def __init__(self, start, end, vert, num):
        self.start = start
        self.end = end
        self.length = (end[0] - start[0]) + (end[1] - start[1]) + 1
        self.vertical = vert
        self.number = num
        self.collisions =[]

    def __str__(self):
        return str(self.start)+ str(self.end)+ " "+str(self.number)+" "+self.get_direction()
    
    def get_direction(self):
        if self.vertical:
            return "down"
        else:
            return "across"


class Word(object):
    def __init__(self, coord, word_tuple):
        self.coord = coord
        self.text = word_tuple[0]
        self.clue = word_tuple[1]

    def __str__(self):
        return self.text

class Board(object):
    def __init__(self, shape, debug=False):
        self.shape = shape
        self.generated = shape
        self.coords = []
        self.width = len(shape[0])
        self.height = len(shape)
        self.collision_list = []
        self.debug = debug
        self.iterations = 0

    def add_coord(self, coord):
        self.coords.append(coord)

    def get_coords(self):
        return self.coords

    def print_coords(self):
        for coord in self.coords:
            print(coord.start, coord.end, coord.length, coord.number, coord.get_direction())
            for ccoord in coord.collisions:
                print(ccoord)
    
    def print_board(self):
        for row in self.generated:
            print("|",end="")
            for item in row:
                if str(item)[0]=="X":
                    print(" ",end="|")
                else:
                    print(str(item)[0], end='|')
            print()
        print()
    
    def print_iterations(self):
        if self.debug:
            print("Number of iterations:",self.iterations)
        else:
            print("Run in debug mode to track iterations")

def generate_coordinates(crossword):
    num_rows = crossword.height
    num_cols = crossword.width
    horizontal_num = 1
    vertical_num = 1


    # find coords by row
    for r in range(num_rows):
        start = None
        end = None
        for c in range(num_cols):
            # start a new word
            if crossword.shape[r][c]=='-' and not start:
                # it isn't just one character
                if c+1 < num_cols and crossword.shape[r][c+1] != 'X':
                    start = (r,c)
                    crossword.shape[r][c]=horizontal_num
                else:
                    continue
            # continue word
            if start and not end:
                crossword.shape[r][c]=horizontal_num
                # This is the last letter
                if (c+1==num_cols or crossword.shape[r][c+1]=='X'):
                        end = (r,c)
                        h_coord = Coord(start, end, False, horizontal_num)
                        crossword.add_coord(h_coord)
                        horizontal_num+=1
                        start = None
                        end = None
                        continue
                #print(r, "  ", c)
        
    #print("---------------")

    # find coords by col
    for c in range(num_cols):
        start = None
        end = None
        for r in range(num_rows):
             # start a new word, either the across number or '-'
            if (isinstance(crossword.shape[r][c], int) or crossword.shape[r][c]=='-') and not start:
                # it isn't just one character
                if r+1 < num_rows and crossword.shape[r+1][c] != 'X':
                    start = (r,c)
                else:
                    continue
            # continue word
            if start and not end:
                # This is the last letter
                if (r+1==num_rows or crossword.shape[r+1][c]=='X'):
                        end = (r,c)
                        v_coord = Coord(start, end, True, vertical_num)

                        # collisions
                        for x in range(start[0],end[0]+1):
                            if (isinstance(crossword.shape[x][c], int)):
                                crossword.coords[crossword.shape[x][c]-1].collisions.append(v_coord)
                                v_coord.collisions.append(crossword.coords[crossword.shape[x][c]-1])
                        crossword.add_coord(v_coord)
                        vertical_num+=1
                        start = None
                        end = None
                        continue
            #print(r, "  ", c)

# recursively gets collisions, typical usage starts at coords[0]
def generate_collisions(board, coord):
    if coord not in board.collision_list:
        if board.debug:
            print("generating ",coord)
        board.collision_list.append(coord)
        for coll in coord.collisions:
            generate_collisions(board,coll)
    else:
        return

def generate_crossword(board, wordlist):
    
    #tried_words = set()

    generate_collisions(board, board.coords[0])
    colls = board.collision_list

    find_and_place(board,board,colls,wordlist)

    #for coord in colls:
        #print("c- ", coord)
    return board
    
def find_and_place(board, new_board, collision_list, wordlist):

    if board.debug:
        board.iterations +=1

    if board.debug and len(collision_list) > 0:
        print("----------START --------------",collision_list[0],"LENGTH:",len(collision_list))

    found = False
    copy = deepcopy(new_board)

    # we handled all collisions
    if collision_list==[]:
        #print("MADE IT TO EMPTY LIST")
        board.generated = new_board.generated
        return True

    constraints = ""
    # only add the first character of the constraint in the case that it is a two+ digit number
    for x in range(collision_list[0].length):
        if collision_list[0].vertical:
            constraints += str(copy.generated[collision_list[0].start[0]+x][collision_list[0].start[1]])[0]
        else:
            constraints += str(copy.generated[collision_list[0].start[0]][collision_list[0].start[1]+x])[0]

    # Generate regex from the constraints
    regex = ""
    for char in constraints:
        if char in string.ascii_lowercase:
            regex+=char
        else:
            regex+="."

    if board.debug:
        print("constraints are:", constraints,"->",regex)
        
    found_matches = [word for word in wordlist[len(constraints)-2] if re.match(regex, word[0]) is not None]

    random.shuffle(found_matches)

    for word in found_matches:
        # place the word down
        for x in range(collision_list[0].length):
            #print(x)
            #print(word[0][x])
            #print(collision_list[0].start[0], " ", collision_list[0].start[1])
            if collision_list[0].vertical:
                copy.generated[collision_list[0].start[0]+x][collision_list[0].start[1]] = word[0][x]
            else:
                copy.generated[collision_list[0].start[0]][collision_list[0].start[1]+x] = word[0][x]
        
        if board.debug:
            copy.print_board()
        found = find_and_place(board,copy,collision_list[1:], wordlist)
        if found:
            #print("-------------------------------------------------------------------- found")
            return True
        #print("Returning False for:",word)
    return False




def main():

    # Wordlist is a 2d list of tuples
    # 0 index is two letter words, max length of 16 letters at index 14
    wordlist = [[] for x in range(15)]

    #----- Known solution to test5
    filename = "nytimes.txt"
    f=open(filename,'r')
    definition = "Testing values"
    lines = f.readlines()
    for word in lines:
        #print(word.strip())
        wordlist[len(word.strip())-2].append((word.strip(),definition))
    f.close()
    #------------------------------

    # TODO: write known solution to test6

    filename = "crosswordwords.txt"
    f = open(filename, "r")

    # This will import words without definitions
    definition = "Testing values"
    lines = f.readlines()
    for word in lines:
        wordlist[len(word.strip())-2].append((word.strip(),definition))
    f.close()

    #------------------------------
    filename = "vocab.txt"
    f = open(filename, "r")

    # This will import words without definitions
    lines = f.readlines()
    for word, definition in zip(lines[0::2], lines[1::2]):
        wordlist[len(word.strip())-2].append((word.strip(),definition.strip()))
    f.close()

    # words2 is 10k words ---------
    filename = "words2.txt"
    f = open(filename, "r")

    # This will import words without definitions
    definition = "Testing values"
    lines = f.readlines()
    for word in lines:
        if len(word) <2 or len(word) > 14:
            continue
        wordlist[len(word.strip())-2].append((word.strip(),definition))
    f.close()

    # Sort all words within each wordlength
    #for words in wordlist:
        #words.sort()


    test = ["----x---",
            "----x---",
            "--------",      
            "xxxxx---",  
            "-----xxx",   
            "--------",
            "----x---",
            "----x---"
            ]

    test2 = ["----x---",
            "----x---",
            "--------",      
            "xxxxx---",
            ]

    test3 = [["-","-","-","X","X","-","-","-"],
            ["-","-","-","X","-","-","-","-"],
            ["-","-","-","-","-","-","-","-"],
            ["-","X","X","-","X","-","X","X"],
            ["-","-","-","X","X","-","-","-"],
            ["-","-","-","-","X","-","-","-"],
            ["-","-","-","-","X","-","-","-"]]

    test4 = [["-","-","-","X","X"],
            ["-","X","X","-","-"],
            ["-","-","-","-","-"],
            ["-","X","X","-","X"],
            ["-","-","-","-","X"],
            ["-","X","X","X","X"],
            ["-","-","-","-","X"]]

    blank = [["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-",]]


    # https://www.nytimes.com/svc/crosswords/v2/puzzle/10386.ans.pdf
    # FRI, Oct 9, 2015
    test5 = [["-","-","-","-","X","X","-","-","-","-","X","-","-","-","-",],
            ["-","-","-","-","-","X","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","X","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","X",],
            ["-","-","-","-","-","-","-","X","X","X","X","-","-","-","-",],
            ["X","X","X","-","-","-","X","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","X","-","-","-","-","-","-","X","-","-","-",],
            ["-","-","-","X","-","-","-","-","-","-","-","X","-","-","-",],
            ["-","-","-","X","-","-","-","-","-","-","X","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","X","-","-","-","X","X","X",],
            ["-","-","-","-","X","X","X","X","-","-","-","-","-","-","-",],
            ["X","-","-","-","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","X","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","X","-","-","-","-","-",],
            ["-","-","-","-","X","-","-","-","-","X","X","-","-","-","-",]]

    # https://www.washingtonpost.com/crossword-puzzles/daily/
    # WED, Nov 10, 2021
    test6 = [["-","-","-","-","-","X","-","-","-","-","X","-","-","-","-",],
            ["-","-","-","-","-","X","-","-","-","-","X","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","X","-","-","-","-",],
            ["-","-","-","-","X","-","-","-","-","X","-","-","-","-","-",],
            ["-","-","-","X","-","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","-","X","X","X","X","-","-","-","-","-","-",],
            ["-","-","-","-","-","X","-","-","-","-","X","X","-","-","-",],
            ["X","X","X","-","-","-","-","-","-","-","-","-","X","X","X",],
            ["-","-","-","X","X","-","-","-","-","X","-","-","-","-","-",],
            ["-","-","-","-","-","-","X","X","X","X","-","-","-","-","-",],
            ["-","-","-","-","-","-","-","-","-","-","-","X","-","-","-",],
            ["X","-","-","-","-","X","-","-","-","-","X","-","-","-","-",],
            ["-","-","-","-","X","-","-","-","-","-","-","-","-","-","-",],
            ["-","-","-","-","X","-","-","-","-","X","-","-","-","-","-",],
            ["-","-","-","-","X","-","-","-","-","X","-","-","-","-","-",]]

    mini1 = [["X","-","-","-","-"],
            ["X","-","-","-","-"],
            ["-","-","-","-","-"],
            ["-","-","-","-","-"],
            ["-","-","-","-","-"]]

    mini2 = [["-","-","-","-","X"],
            ["-","-","-","-","X"],
            ["-","-","-","-","-"],
            ["X","-","-","-","-"],
            ["X","-","-","-","-"]]

    mini3 = [["-","-","-","-","-"],
            ["-","X","-","-","-"],
            ["-","X","-","-","-"],
            ["-","X","-","-","-"],
            ["-","X","-","-","-"]]


    crossword = Board(test4, True)
    crossword.print_board()
    generate_coordinates(crossword)
    generate_crossword(crossword, wordlist)    
    crossword.print_board()
    crossword.print_iterations()

    print("Time taken:",time.time() - start_time)


if __name__ == "__main__":
    main()