from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor
from extract_keywords import final_keywords


def set_sentances(text):
    print("3.Selecting Sentences based on keywords...")
    sentences = [sent_tokenize(text)]
    # nested list to single list
    sentences = [i for sent in sentences for i in sent]

    # remove short sentences
    sentences = [sent.strip() for sent in sentences if len(sent) > 20]
    # print(sentences)
    return sentences


def extract_sentences(text, quantity):
    keywords, text = final_keywords(text, quantity)
    key_processor = KeywordProcessor()
    filtered_sentences = {}

    # adding keywords to processor and to dict
    for i in keywords:
        filtered_sentences[i] = []
        key_processor.add_keyword(i)

    # calling fn to set sentences from summary text
    sentences = set_sentances(text)
    print("4.Filtering sentences...")
    # extracting sentences with given keywords and add to dict keys
    for sent in sentences:
        keyword_searched = key_processor.extract_keywords(sent)
        for key in keyword_searched:
            filtered_sentences[key].append(sent)
    filtered_sentences = dict([(key, val) for key, val in filtered_sentences.items() if (val)])

    # sorting with longest sentence of given keyword on top
    for i in filtered_sentences.keys():
        values = filtered_sentences[i]
        values = sorted(values, key=len, reverse=True)
        filtered_sentences[i] = values

    print(filtered_sentences)
    return filtered_sentences

# text = "Sniffer dog Tucker uses his nose to help researchers find out why a killer whale population off the northwest coast of the United States is on tKe decline. He searches for whale faeces floating on the surface of the water, which are then collected for examination. He is one of the elite team of detection dogs used by scientists studying a number of species including right whales and killer whales.Conservation canines are fast becoming indispensable tools for biologists according to Aimee Hurt, associate director and co-founder of Working Dogs for Conservation, based in Three Forks, Montana.Over the last few years, though, so many new conservation dog projects have sprung up that Hurt can no longer keep track of them all. Her organization’s dogs and their handlers are fully booked to assist field researchers into 2012.“Dogs have such a phenomenal sense of smell”, explained Sam Wasser, director of the Center for Conservation biology at the University of Washington in Seattle. He has worked with scat-detection dogs since 199(g). Scientists have been using Conservation Canines in their research since 199(g). These dogs have enabled them to non-invasively access vast amount of genetic and physiological information which is used to tackle conservation problems around the world. Such information has proved vital for determining the causes and consequences of human disturbances on wildlife as well as the actions needed to mitigate such impacts.The ideal detection dog is extremely energetic with an excessive play drive. These dogs will happily work all • day long, motivated by the expectation of a ball game as a reward for sample detection. The obsessive, high energy personalities of detection dogs also make them difficult to maintain as pets. As a result, they frequently find themselves abandoned to animal shelters, facing euthanasia. The programme rescues these dogs and offers them a satisfying career in conservation research."

# print(extract_sentences(text, 1))