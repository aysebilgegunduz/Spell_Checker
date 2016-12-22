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

def dictToFile(dict_list, mapping):

    thefile = open('test.txt', 'w')
    for i in sorted(mapping):
        thefile.write("%s " % i)
    thefile.write("\n")
    for i in sorted(mapping):
        for j in sorted(mapping):
            thefile.write("%s " % dict_list[i][j])
        thefile.write("\n")
    return None

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
    dictToFile(emission_list, mapping)
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

def FP_TN_words(test, result):
    """
    dogru yanlis harf sayisini hesapla
    :param train:
    :param result:
    :return:
    """
    fp = 0
    tn = 0
    for i in range(len(test)):
        if(test[i][0] != '_' and test[i][0] == result[i]):
            fp += 1
        elif(test[i][0] != '_' and test[i][0] != result[i]):
            tn += 1
    return fp, tn
def b_FP_TN_words(train):
    """
    dogru yanlis harf sayisini hesapla
    :param train:
    :param result:
    :return:
    """
    fp = 0
    tn = 0
    for i in range(len(train)):
        if(train[i][0] != '_' and train[i][0] == train[i][1]):
            fp += 1
        elif(train[i][0] != '_' and train[i][0] != train[i][1]):
            tn += 1
    return fp, tn
def b_FP_TN_sentence(train):
    """
    dogru ve yanlis ogrenilmis kelime sayisi
    :param train:
    :param result:
    :return:
    """
    fp = 0
    tn = 0
    tmp_t = ""
    tmp_r = ""
    for i in range(len(train)):
        if(train[i][0] != '_'):
            tmp_t += train[i][0]
            tmp_r += train[i][1]
        elif(train[i][0] == '_'):
            if(tmp_t == tmp_r and tmp_t !="" and tmp_r != ""):
                fp += 1
            elif(tmp_t != tmp_r and tmp_t !="" and tmp_r != ""):
                tn += 1
            tmp_r = ""
            tmp_t = ""
    return fp, tn

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
result = viterbi(init_prob, trans_prob, em_prob,test, mapping)
fp_s_b, tn_s_b = b_FP_TN_sentence(train)
fp_w_b, tn_w_b = b_FP_TN_words(train)
fp_w, tn_w = FP_TN_words(test,result)
print("sirasiyla dogru ve yanlis kelime sonuclari: ", fp_s_b, tn_s_b, (fp_s_b/(fp_s_b+tn_s_b)))
print("sirasiyla dogru ve yanlis harf sonuclari: ", fp_w_b, tn_w_b, (fp_w_b/(fp_w_b+tn_w_b)))
print("Viterbi'den sonra sirasiyla dogru ve yanlis kelime sonuclari: ", fp_w, tn_w, (fp_w/(fp_w+tn_w)))
a = 1

