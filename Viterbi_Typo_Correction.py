import sys
import string
import math
import pdb
import pandas as pd

numofchars = 1
mapping = {char: value for value, char in enumerate(string.ascii_lowercase)}
reversemapping = dict(enumerate(string.ascii_lowercase))

initialProbs = [1] * 26
charactercount = [1] * 26
outputtransitions = [[1 for i in range(26)] for j in range(26)]
statetransitions = [[1 for i in range(26)] for j in range(26)]
outputProbs = [[1 for i in range(26)] for j in range(26)]
stateProbs = [[1 for i in range(26)] for j in range(26)]
maxProbabilityState = dict()
maxProbabilityOut = dict()


def getData(filename):
    global numofchars
    infile = open(filename)
    index = 0
    prevOrigLetter = 'd'
    #  Training loop for data
    for line in infile:  # Iterate through lines of file
        if '..' in line:  # If its the end of training data
            break

        words = line.split()
        if index == 0:  # If its the first char
            charactercount[mapping[words[0]]] += 1
            index += 1
        elif words[0] == '_':  # If the start of a new word
            index = 0  # Reset index
        else:  # If in the middle of a word
            statetransitions[mapping[prevOrigLetter]][mapping[words[0]]] += 1
            outputtransitions[mapping[words[0]]][mapping[words[1]]] += 1
            index += 1
            # print("statetransitions[",mapping[prevOrigLetter],"][mapping[",words[0],"]")
        prevOrigLetter = words[0]
    infile.close()


def calcProbability():
    global initialProbs, charactercount, outputtransitions, statetransitions
    global outputProbs, stateProbs
    numofchars = sum(charactercount)
    # Calculate all 3 probabilities
    for row in range(0, 26):
        sumofoutputrow = sum(outputtransitions[row])
        sumofstaterow = sum(statetransitions[row])
        for column in range(0, 26):
            outputProbs[row][column] = math.log(outputtransitions[row][column] / sumofoutputrow)
            stateProbs[row][column] = math.log(statetransitions[row][column] / sumofstaterow)
            # print("Storing stateProbs [",row, "][",column,"] is ", math.log(statetransitions[row][column]/sumofstaterow))
        initialProbs[row] = math.log(charactercount[row] / numofchars)


def calcMaxProbability():
    global maxProbabilityOut, maxProbabilityState
    for i, character in enumerate(mapping):
        maxProbabilityState[i] = reversemapping[stateProbs[i].index(max(stateProbs[i]))]
        print(reversemapping[i], " is most likely paired with ", maxProbabilityState[i])


'''
Currently iterating through each character
after '..' and getting the max of the sum
of three different indexes of matrices.
The the state probability from t-1 to x,
from t-1 to t
and output probabilities from 0 to 25 at t
Takes the maximum of this addition and attempts
to turn it into a character
'''


def viterbi(filename):
    testmode = True
    viterbi = [{}]
    path = {}
    newOutput = ""
    prevOrigLetter = "b"  # Dummy character

    for line in filename:  # Iterate through remaining lines for testing
        if ('.' in line):
            testmode = True
        elif (testmode):
            char = line.split()[0]
            for i in range(26):
                viterbi[0][i] = initialProbs[i] * outputProbs[i][mapping[line.split()[0]]]
                # Add a list containing current the current char
                path[y] = [y]

            if (prevOrigLetter == "_"):
                for i in range(26):
                    viterbi[0][i] = initialProbs[i] * outputProbs[i][mapping[char]]
                    # Add a list containing current the current char
                    path[y] = [y]


            else:
                # probability, mostLikelyChar = (max(( viterbi[mapping[prevOrigLetter]][x] + stateProbs[x][mapping[char]] + outputProbs[x][mapping[char]], x)  for x in range(26)))
                # viterbi[i][mapping[char]] = probability
                pdb.set_trace()
                viterbi.append({})  # Add a new dictionary
                newpath = {}
                for i in range(26):
                    # Sets the probability to viterbi[t-1][x] plus stateprobs[x][t] plus outputprobs[x][t]
                    probability, mostLikelyChar = (max((viterbi[mapping[prevOrigLetter]][x] + stateProbs[x][
                        mapping[char]] + outputProbs[i][mapping[char]], x) for x in range(26)))
                    viterbi[char][i] = probability
                    newpath[i] = path[mostLikelyChar] + [i]

                path = newpath
                print(path)

            prevOrigLetter = char


def main():
    getData(sys.argv[1])
    calcProbability()
    calcMaxProbability()
    viterbi(sys.argv[1])
    print("The count of characters is: ", charactercount)


main()