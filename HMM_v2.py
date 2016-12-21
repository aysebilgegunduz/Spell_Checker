from hmmlearn import hmm
import numpy as np
import pandas as pd
import string
import operator
import copy

"""
1. 0 olasılık değeri donmesin Laplace Smoothing hepsine mi yapilmali ? Yoksa sadece 0 donenlere mi?
"""

def Start_with_prob(train, mapping, sth_counter):
    """
    {Si ile baslayan diziler} / {tum diziler}
    :param train:
    :param mapping:
    :param sth_counter:
    :return:
    """
    i = 0
    str_list=[]
    tmp = ""
    I = {}
    str_list.append(train[0][0])
    for i in range(len(train)):
        if(train[i][0] == '_'):
            str_list.append(train[i+1][0])
    for i in mapping:
        I[i] =(str_list.count(i) + 1) / (len(str_list) +(len(train) - sth_counter)) # laplacian smoothing kullandim.
    return I

def Transition_prob(train, mapping, sth_counter):
    """
    {Si den Sjye gecisler} / {Si den tum gecisler}
    :param train:
    :param mapping:
    :param sth_counter:
    :return:
    """
    #create nested mapping list
    trans_list = {}
    for i in mapping:
        trans_list[i] = {}
        for j in mapping:
            trans_list[i][j]=0
    for i in range(len(train)-1):
        if(train[i][0] != '_' and train[i+1][0] != '_'):
            trans_list[train[i][0]][train[i+1][0]] += 1
    prob = 0
    tmp_prob = {}
    for i in mapping:
        for j in mapping:
            prob += trans_list[i][j]
        tmp_prob[i] = prob
        prob = 0
    trans_list = laplace_smoothing(trans_list, tmp_prob,len(train)-sth_counter, mapping)
    return trans_list

def Emission_prob(train, mapping, sth_counter):
    # create nested mapping list
    emission_list = {}
    tmp_emission_list = {}
    tmpList = copy.deepcopy(train)
    tmpList = np.asarray(tmpList).T.tolist()
    for i in mapping:
        emission_list[i] = {}
        tmp_emission_list[i] = tmpList[0].count(i)
        for j in mapping:
            emission_list[i][j] = 0
    for i in range(len(train)):
        if(train[i][0] != '_'):
            emission_list[train[i][0]][train[i][1]] += 1 #a harfi gorulmesi gerekirken b harfinin gorulmesi
    #Laplace Smoothing part
    emission_list = laplace_smoothing(emission_list, tmp_emission_list, len(train)-sth_counter, mapping)
    return emission_list

def laplace_smoothing(prob, tmp_prob, vocab_num, mapping):
    for i in mapping:
        for j in mapping:
            prob[i][j] = (prob[i][j] + 1) / (tmp_prob[i] + vocab_num)
    return prob

def viterbi(init_prob, trans_prob, em_prob, test, mapping):
    """

    :param init_prob:
    :param trans_prob:
    :param em_prob:
    :param test:
    :param mapping:
    :return:
    """
    #test[i][0][1] includes wrong part
    char_list = ""
    tmp_list = {}
    val, v_init = viterbi_init(init_prob, em_prob, test[0][1], mapping)
    char_list += val[0]
    for i in range(1, len(test)):
        if(test[i][1] != '_'):
            for j in mapping:
                val, _ = viterbi_init(v_init, trans_prob,test[i][1], mapping)
                tmp_list[j] = val[1]*em_prob[test[i][1]][j]
            tmp = max(tmp_list.items(), key=operator.itemgetter(1))
            char_list += tmp[0]
            v_init = tmp_list
            tmp_list = {}
        else:
            char_list += '_'



    return char_list

def viterbi_init(I, prob, test, mapping):
    """
    initial icin prob yerine emission prob gonderildi digerleri icin transition prob
    :param I:
    :param prob:
    :param test:
    :param mapping:
    :return:
    """
    v_init = {}
    for i in mapping:
        v_init[i] = I[i] * prob[test][i]
    val = max(v_init.items(), key=operator.itemgetter(1))

    return val, v_init


#import matplotlib.pyplot as plt
sth_counter = 0 # _ _ lerin sayisina bakilacak
docs = pd.read_csv("docs.csv", header=None)
test = docs.values[0:19999,:]
train = docs.values[19999:,:]
mapping = { char:value for value,char in enumerate(string.ascii_lowercase)}
#reversemapping = dict(enumerate(string.ascii_lowercase))
for i in range(len(train)):
    if (train[i][0] == '_'):
        sth_counter += 1
init_prob = Start_with_prob(train, mapping, sth_counter)
trans_prob = Transition_prob(train, mapping, sth_counter)
em_prob = Emission_prob(train, mapping, sth_counter)
viterbi(init_prob, trans_prob, em_prob,test, mapping)
a = 1

