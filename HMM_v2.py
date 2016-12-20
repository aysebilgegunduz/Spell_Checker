from hmmlearn import hmm
import numpy as np
import pandas as pd
import string
import operator

def Start_with_prob(train, mapping, sth_counter):
    i = 0
    str_list=[]
    tmp = ""
    I = {}
    str_list.append(train[0][0][0])
    for i in range(len(train)):
        if(train[i] == '_ _'):
            str_list.append(train[i+1][0][0])
    for i in mapping:
        I[i] =str_list.count(i) /(len(train) - sth_counter) #buradan emin degilim hep en basta baslayanlara bolumu mudur yoksa total mi?__'ler cikarildi
    return I

def Transition_prob(train, mapping, sth_counter):
    #create nested mapping list
    trans_list = {}
    for i in mapping:
        trans_list[i] = {}
        for j in mapping:
            trans_list[i][j]=0
    for i in range(len(train)-1):
        if(train[i][0][0] != '_' and train[i+1][0][0] != '_'):
            trans_list[train[i][0][0]][train[i+1][0][0]] += 1/(len(train)-sth_counter)
    #olasilik hesaplanacak !!!!!!
    return trans_list

def Emission_prob(train, mapping, sth_counter):
    # create nested mapping list
    emission_list = {}
    for i in mapping:
        emission_list[i] = {}
        for j in mapping:
            emission_list[i][j]=0
    for i in range(len(train)):
        #if(train[i][0][0] != train[i][0][2]):
        if(train[i][0][0] != '_'):
            emission_list[train[i][0][2]][train[i][0][0]] += 1/(len(train)-sth_counter)
    # olasilik hesaplanacak !!!!!!
    return emission_list

def viterbi(init_prob, trans_prob, em_prob, test, mapping):
    #test[i][0][1] includes wrong part
    char_list=[]
    for i in range(len(test)):
        val, v_init = viterbi_init(init_prob, em_prob, test[i][0][2], mapping)
        char_list.append(val[0])
    return None

def viterbi_init(I, em_prob, test, mapping):
    v_init = {}
    for i in mapping:
        v_init[i] = I[i] * em_prob[test][i]
    val = max(v_init.items(), key=operator.itemgetter(1))
    a=1

    return val, v_init


#import matplotlib.pyplot as plt
sth_counter = 0 # _ _ lerin sayisina bakilacak
docs = pd.read_csv("docs.csv", header=None)
test = docs.values[0:19999,:]
train = docs.values[19999:,:]
mapping = { char:value for value,char in enumerate(string.ascii_lowercase)}
#reversemapping = dict(enumerate(string.ascii_lowercase))
for i in range(len(train)):
    if (train[i] == '_ _'):
        sth_counter += 1
init_prob = Start_with_prob(train, mapping, sth_counter)
trans_prob = Transition_prob(train, mapping, sth_counter)
em_prob = Emission_prob(train, mapping, sth_counter)
viterbi(init_prob, trans_prob, em_prob,test, mapping)
a = 1

