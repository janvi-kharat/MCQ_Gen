import requests
import re
import random
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from nltk.corpus import wordnet
from find_sentances import extract_sentences
import pandas as pd




def wordnet_distractors(syon, word):
    print("6.Obtaining relative options from Wordnet...")
    distractors = []
    word = word.lower()
    original_word = word
    # checking if word is more than one word then make it one word with _
    if len(word.split()) > 0:
        word = word.replace(" ", "_")
    hypersyon = syon.hypernyms()
    if (len(hypersyon) == 0):
        return distractors
    for i in hypersyon[0].hyponyms():
        name = i.lemmas()[0].name()
        if (name == original_word):
            continue
        name = name.replace("_", " ")
        name = " ".join(i.capitalize() for i in name.split())
        if name is not None and name not in distractors:
            distractors.append(name)
    return distractors


def conceptnet_distractors(word):
    print("6.Obtaining relative options from ConceptNet...")
    word = word.lower()
    original_word = word
    if (len(word.split()) > 0):
        word = word.replace(" ", "_")
    distractor_list = []
    url = "http://api.conceptnet.io/query?node=/c/en/%s/n&rel=/r/PartOf&start=/c/en/%s&limit=5" % (word, word)
    obj = requests.get(url).json()
    for edge in obj['edges']:
        link = edge['end']['term']
        url2 = "http://api.conceptnet.io/query?node=%s&rel=/r/PartOf&end=%s&limit=10" % (link, link)
        obj2 = requests.get(url2).json()
        for edge in obj2['edges']:
            word2 = edge['start']['label']
            if word2 not in distractor_list and original_word.lower() not in word2.lower():
                distractor_list.append(word2)
    return distractor_list


def word_sense(sentence, keyword):
    print("5.Getting word sense to obtain best MCQ options with WordNet...")
    word = keyword.lower()
    if len(word.split()) > 0:
        word = word.replace(" ", "_")
    syon_sets = wordnet.synsets(word, 'n')
    if syon_sets:
        try:
            wup = max_similarity(sentence, word, 'wup', pos='n')
            adapted_lesk_output = adapted_lesk(sentence, word, pos='n')
            lowest_index = min(syon_sets.index(wup), syon_sets.index(adapted_lesk_output))
            return syon_sets[lowest_index]
        except:
            return syon_sets[0]
    else:
        return None


def display(text, quantity):
    print("hello")
    filtered_sentences = extract_sentences(text, quantity)
    options_for_mcq = {}
    print("using wordsense")
    for keyword in filtered_sentences:
        wordsense = word_sense(filtered_sentences[keyword][0], keyword)
        if wordsense:
            distractors = wordnet_distractors(wordsense, keyword)
            if len(distractors) > 0:
                options_for_mcq[keyword] = distractors
            if len(distractors) < 4:
                distractors = conceptnet_distractors(keyword)
                if len(distractors) > 0:
                    options_for_mcq[keyword] = distractors
        else:
            distractors = conceptnet_distractors(keyword)
            if len(distractors) > 0:
                options_for_mcq[keyword] = distractors
    print("7. Creating JSON response for API...")
    df = pd.DataFrame()
    cols = ['question', 'options', 'extras', 'answer']
    index = 1
    print("**********************************************************************************")
    print("NOTE: Human intervention is required to correct some of the generated MCQ's ")
    print("************************************************************************************\n\n")
    for i in options_for_mcq:
        sentence = filtered_sentences[i][0]
        sentence = sentence.replace("\n", '')
        pattern = re.compile(i, re.IGNORECASE)
        output = pattern.sub(" ______ ", sentence)
        print("%s)" % (index), output)
        options = [i.capitalize()] + options_for_mcq[i]
        top4 = options[:4]
        random.shuffle(top4)
        optionsno = ['a', 'b', 'c', 'd']
        for idx, choice in enumerate(top4):
            print("\t", optionsno[idx], ")", " ", choice)
        print("\nMore options: ", options[4:8], "\n\n")
        # i want to add all questions to a dataframe

        df = df.append(pd.DataFrame([[output, top4, options[4:8], i.capitalize()]], columns=cols))
        index = index + 1
    df.to_json('response.json', orient='records', force_ascii=False)


# text = "Sniffer dog Tucker uses his nose to help researchers find out why a killer whale population off the northwest coast of the United States is on tKe decline. He searches for whale faeces floating on the surface of the water, which are then collected for examination. He is one of the elite team of detection dogs used by scientists studying a number of species including right whales and killer whales.Conservation canines are fast becoming indispensable tools for biologists according to Aimee Hurt, associate director and co-founder of Working Dogs for Conservation, based in Three Forks, Montana.Over the last few years, though, so many new conservation dog projects have sprung up that Hurt can no longer keep track of them all. Her organization’s dogs and their handlers are fully booked to assist field researchers into 2012.“Dogs have such a phenomenal sense of smell”, explained Sam Wasser, director of the Center for Conservation biology at the University of Washington in Seattle. He has worked with scat-detection dogs since 199(g). Scientists have been using Conservation Canines in their research since 199(g). These dogs have enabled them to non-invasively access vast amount of genetic and physiological information which is used to tackle conservation problems around the world. Such information has proved vital for determining the causes and consequences of human disturbances on wildlife as well as the actions needed to mitigate such impacts.The ideal detection dog is extremely energetic with an excessive play drive. These dogs will happily work all • day long, motivated by the expectation of a ball game as a reward for sample detection. The obsessive, high energy personalities of detection dogs also make them difficult to maintain as pets. As a result, they frequently find themselves abandoned to animal shelters, facing euthanasia. The programme rescues these dogs and offers them a satisfying career in conservation research."
#
# display(text,1)