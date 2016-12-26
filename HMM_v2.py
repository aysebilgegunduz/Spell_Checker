
import numpy as np
import pandas as pd
import string
import operator
import copy


"""
1. 0 olasılık değeri donmesin diye Laplace Smoothing hepsine uygulandi.
"""

def Start_with_prob(train, mapping, sth_counter):
    """
    {Si ile baslayan diziler} / {tum diziler}
    :param train: 20.000'den itibaren tüm veriler
    :param mapping: a-z arasındaki tüm harfler
    :param sth_counter: _ isaretinin train set icerisinde kac adet bulundugu
    :return: I : ilk durum olasiliklari
    """
    str_list=[]
    I = {}
    str_list.append(train[0][0])
    #_ isaretlerinin hemen sonrasındaki harfler bir listeye eklendi.
    for i in range(len(train)):
        if(train[i][0] == '_'):
            str_list.append(train[i+1][0])
    # kelimelerin basladigi harfler listesindeki harf sayilari a-z'ye kadar sayilarak
    # I hash tablosuna yerlestirildi. 0 olasilik degeri cikmasin diye laplace smoothing kullanildi.
    for i in mapping:
        I[i] =(str_list.count(i) + 1) / (len(str_list) +(len(train) - sth_counter)) # laplacian smoothing kullandim.
    return I

def Transition_prob(train, mapping, sth_counter):
    """
    {Si den Sjye gecisler} / {Si den tum gecisler}
    :param train: 20.000'den itibaren tüm veriler
    :param mapping: a-z arasındaki tüm harfler
    :param sth_counter: _ isaretinin train set icerisinde kac adet bulundugu
    :return: trans_list: Durum gecis olasilik matrisi
    """
    #ic ice gecmis a-z'ye degerler iceren ilk deger karsiliklari da 0 olan bir hash tablosu (pythonda bunlarin ismi dictionary)
    #hazirlandi.
    trans_list = {}
    for i in mapping:
        trans_list[i] = {}
        for j in mapping:
            trans_list[i][j]=0
    #train listteki dogru kelime sutunu kullanilarak bir harften sonra baska bir harfin gelme sayisi bulundu
    for i in range(len(train)-1):
        if(train[i][0] != '_' and train[i+1][0] != '_'):
            trans_list[train[i][0]][train[i+1][0]] += 1
    #bir harften sonra baska bir harfin gelme olasiligi hesaplandi. Laplace smoothing kullanildi.
    prob = 0
    tmp_prob = {}
    for i in mapping:
        for j in mapping:
            prob += trans_list[i][j]
        tmp_prob[i] = prob
        prob = 0
    trans_list = laplace_smoothing(trans_list, tmp_prob,len(train)-sth_counter, mapping)
    #odevde bu olusturulan olasiliklar istendigi icin dictToFile() fonksiyonu cagriliyor, ihtiyac oldugunda.
    #dictToFile(trans_list, mapping)
    return trans_list

def dictToFile(dict_list, mapping):
    #odevde olasiliklarin degerleri istendigi icin bu fonksiyon olusturuldu. dictionary degerlerine gore olasilik degerlerini
    #dosyaya yerlestiriyor.
    thefile = open('test.txt', 'w')
    for i in sorted(mapping):
        thefile.write("%s " % i)
    thefile.write("\n")
    #goruntu duzgun gorunsun diye 0.'den sonraki 5 digit aliniyor.
    for i in sorted(mapping):
        for j in sorted(mapping):
            thefile.write("%.5f " % dict_list[i][j])
        thefile.write("\n")
    return None

def Emission_prob(train, mapping, sth_counter):
    """
    :param train: 20.000'den itibaren tüm veriler
    :param mapping: a-z arasındaki tüm harfler
    :param sth_counter: _ isaretinin train set icerisinde kac adet bulundugu
    :return: emission_list: Cikis Olasilik Matrisi
    """
    # create nested mapping list
    emission_list = {}
    tmp_emission_list = {}
    #traindeki veri tmpList'e kopyalandi copy.deepcopy() kullanilmadiginda python sadece referans kopyaliyor.
    #Bu noktada da tmpList'teki deger degistiginde train'deki deger de degisiyor.
    tmpList = copy.deepcopy(train[:,0])
    #daha kolay islem yapabilmek icin Transpose yapip tekrar listeye cevirdim
    tmpList = np.asarray(tmpList).T.tolist()
    for i in mapping:
        emission_list[i] = {}
        #bunu olasilik hesabinda kullanmak icin her harfin train'de kac defa gectigini bulmak amacli kullaniyorum
        tmp_emission_list[i] = tmpList.count(i)
        for j in mapping:
            emission_list[i][j] = 0
    # her harf icin biri goruldugunde digerinin gorulme olasiligi hesaplaniyor
    # hesaplama kelime bazinda yapiliyor as_ben ornegi icin sira s'ye geldiginde
    # s den sonra b gelme olasiligi hesaplanmiyor. b ye gecilip b den sonra e gelme olasiligi seklinde hesaplaniyor.s
    for i in range(len(train)):
        if(train[i][0] != '_'):
            emission_list[train[i][0]][train[i][1]] += 1 #a harfi gorulmesi gerekirken b harfinin gorulmesi
    #Laplace Smoothing ile cikis olasilik matrisi hesaplaniyor.
    emission_list = laplace_smoothing(emission_list, tmp_emission_list, len(train)-sth_counter, mapping)
    # odevde bu olusturulan olasiliklar istendigi icin dictToFile() fonksiyonu cagriliyor, ihtiyac oldugunda.
    #dictToFile(emission_list, mapping)
    return emission_list

def laplace_smoothing(prob, tmp_prob, vocab_num, mapping):
    #laplace smoothing islemi yapiliyor.
    for i in mapping:
        for j in mapping:
            prob[i][j] = ((prob[i][j] + 1) / (tmp_prob[i] + vocab_num))
    return prob

def viterbi(init_prob, trans_prob, em_prob, test, mapping):
    """

    :param init_prob:
    :param trans_prob:
    :param em_prob:
    :param test:
    :param mapping:
    :return: char_list: son durumda olusturulan karakter listesi
    """
    char_list = ""
    tmp_list = {}
    #baslangic viterbi degeri hesaplaniyor.
    val, v_init = viterbi_init(init_prob, em_prob, test[0][1], mapping)
    char_list += val[0]

    for i in range(1, len(test)):
        # burada da islemler kelimeden harflere indirgeniyor.
        # eger kelime sonlarini hesaba katmayip devam ediyormus gibi harf harf kontrol edersem bir süre sonra
        # olasiliklar 0 a cok yaklastigi icin 0'a indirgeniyor ve bu durumda tum olasiliklar 0 kabul ediliyor.
        # bu yuzden kelime arasi degilse ve kelime baslangici degilse kontrolu yapiliyor.
        if(test[i][1] != '_' and test[i-1][1] != '_'):
            for j in sorted(mapping):
                val, _ = viterbi_init(v_init, trans_prob,test[i][1], mapping)
                tmp_list[j] = (val[1]*em_prob[test[i][1]][j])
            tmp = max(tmp_list.items(), key=operator.itemgetter(1))
            char_list += tmp[0]
            v_init = tmp_list
            tmp_list = {}
        #bu bir kelime baslangici ise ilk initial islemini yap.
        elif test[i-1][1] == '_':
            val, v_init = viterbi_init(init_prob, em_prob, test[i][1], mapping)
            char_list += val[0]
        #bunu son olusturdugum sonuctaki kelimeler anlasilir olsunlar diye ekledim kelime aralarinda _ koyuluyor.
        else:
            char_list += '_'
    return char_list

def viterbi_init(I, prob, test, mapping):
    """
    initialization icin prob yerine emission_prob gonderildi digerleri icin transition_prob kullanilip buradan cikan sonuc ile uygun
    emission probability degeri carpildi.
    :param I: ilk durum olasiliklari
    :param prob: initialization icin b matrisi digerleri icin a matrisi
    :param test: testten elime gelen harf degeri
    :param mapping: a-z arasındaki tum karakterler
    :return: val, v_init: v_init sadece initialization'da kullaniliyor, val degeri max olasilik degeri.
    """

    v_init = {}
    for i in mapping:
        v_init[i] = I[i] * prob[test][i]
    val = max(v_init.items(), key=operator.itemgetter(1))
    #initialization icin gelen maks val degeri aslında hangi karakterin de secilecegini gosteriyor
    #ama sonraki evreler de bu bir de emission prob ile carpilip son durumda tum listeden bulunan maks degeri secilen
    #karakter olarak kullaniliyor.
    return val, v_init

def TP_FN_words(test, result):
    """
    dogru yanlis harf sayisini hesapla
    :param train:
    :param result:
    :return:
    """
    tp = 0
    fn = 0
    for i in range(len(test)):
        if(test[i][0] != '_' and test[i][0] == result[i]):
            tp += 1
        elif(test[i][0] != '_' and test[i][0] != result[i]):
            fn += 1
    return tp, fn
def b_TP_FN_words(train):
    """
    dogru yanlis harf sayisini hesapla
    :param train: test teki kelimeler
    :param result:
    :return:
    """
    tp = 0
    fn = 0
    for i in range(len(train)):
        if(train[i][0] != '_' and train[i][0] == train[i][1]):
            tp += 1
        elif(train[i][0] != '_' and train[i][0] != train[i][1]):
            fn += 1
    return tp, fn
def b_TP_FN_sentence(train):
    """
    dogru ve yanlis ogrenilmis kelime sayisi
    :param train: test gonderiliyor aslinda ismi train sadece
    :param result:
    :return:
    """
    tp = 0
    fn = 0
    tmp_t = ""
    tmp_r = ""
    for i in range(len(train)):
        if(train[i][0] != '_'):
            tmp_t += train[i][0]
            tmp_r += train[i][1]
        elif(train[i][0] == '_'):
            if(tmp_t == tmp_r and tmp_t !="" and tmp_r != ""):
                tp += 1
            elif(tmp_t != tmp_r and tmp_t !="" and tmp_r != ""):
                fn += 1
            tmp_r = ""
            tmp_t = ""
    return tp, fn

def TP_FN_sentence(test, result):
    """
    dogru ve yanlis ogrenilmis kelime sayisi
    :param train: test gonderiliyor aslinda ismi train sadece
    :param result:
    :return:
    """
    tp = 0
    fn = 0
    tmp_t = ""
    tmp_r = ""
    for i in range(len(test)):
        if(test[i][0] != '_'):
            tmp_t += test[i][0]
            tmp_r += result[i]
        elif(test[i][0] == '_'):
            if(tmp_t == tmp_r and tmp_t !="" and tmp_r != ""):
                tp += 1
            elif(tmp_t != tmp_r and tmp_t !="" and tmp_r != ""):
                fn += 1
            tmp_r = ""
            tmp_t = ""
    return tp, fn
sth_counter = 0 # _ lerin sayisina bakilacak
docs = pd.read_csv("docs.csv", header=None)
test = docs.values[0:19999,:]
train = docs.values[19999:,:]
#a-z arasındaki lowecase karakterler
mapping = { char:value for value,char in enumerate(string.ascii_lowercase)}
#kelime aralarının sayisi
for i in range(len(train)):
    if (train[i][0] == '_'):
        sth_counter += 1
init_prob = Start_with_prob(train, mapping, sth_counter)
trans_prob = Transition_prob(train, mapping, sth_counter)
em_prob = Emission_prob(train, mapping, sth_counter)
#son durumda olusturulan cumleler
result = viterbi(init_prob, trans_prob, em_prob,test, mapping)
tp_s_b, fn_s_b = b_TP_FN_sentence(test)
tp_w_b, fn_w_b = b_TP_FN_words(test)
tp_w, fn_w = TP_FN_words(test,result)
tp_s, fn_s = TP_FN_sentence(test,result)

print("Viterbiden önce sirasiyla dogru ve yanlis kelime sonuclari ve basari oranlari: ", tp_s_b, fn_s_b, np.around((tp_s_b/(tp_s_b+fn_s_b)),2))
print("Viterbiden önce sirasiyla dogru ve yanlis harf sonuclari ve basari oranlari: ", tp_w_b, fn_w_b, np.around((tp_w_b/(tp_w_b+fn_w_b)),3))
print("Viterbi'den sonra sirasiyla dogru ve yanlis harf sonuclari ve basari oranlari: ", tp_w, fn_w, np.around((tp_w/(tp_w+fn_w)),3))
print("Viterbi'den sonra sirasiyla dogru ve yanlis kelime sonuclari test ve basari oranlari: ", tp_s, fn_s, np.around((tp_s/(tp_s+fn_s)),3))
