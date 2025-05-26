import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pke
from generate_summary import Summary
stop_words = set(stopwords.words('english'))

def remove_stopwords(text):
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    return " ".join(filtered_text)

# Use the function to remove stopwords from your text

def extracting_keywords(text):
    # Remove stopwords and preprocess text
    text_without_stopwords = remove_stopwords(text)

    # Initialize list to store keywords
    keywords = []

    # Initialize extractor
    extractor = pke.unsupervised.MultipartiteRank()
    extractor.load_document(text_without_stopwords)

    # Specify POS tags for candidate selection
    pos = {'PROPN'}

    # Define stopwords and other filters
    stoplist = list(string.punctuation)
    stoplist += stopwords.words('english')
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']

    # Candidate selection
    extractor.candidate_selection(pos=pos)

    # Candidate weighting
    extractor.candidate_weighting()

    # Get top N keywords
    keyphrases = extractor.get_n_best(n=15)
    for keyphrase in keyphrases:
        keywords.append(keyphrase[0])

    return keywords

def final_keywords(text, quantity):
    keywords_from_fulltext = extracting_keywords(text)
    if (quantity == '0'):
        print("2(a).Generating summary with Transformers.Pls wait!!")
        generated_summary = Summary(text)
        filtered_keywords = []
        for i in keywords_from_fulltext:
            if i.lower() in generated_summary:
                filtered_keywords.append(i)
        print("2(b).Selected Keywords from summary :", filtered_keywords)
        return filtered_keywords, generated_summary
    else:
        print("2.Selected Keywords from Full Text :", keywords_from_fulltext)
        return keywords_from_fulltext, text

# f = open('article.txt','r')
# text = f.read()
# f.close()
# keywords,summary= final_keywords(text)
# these keywords will be used to extract sentences from summary text then blank will
# be given at this keyword place then will use wordnet to get more similar words to give
# options

# text = "Sniffer dog Tucker uses his nose to help researchers find out why a killer whale population off the northwest coast of the United States is on tKe decline. He searches for whale faeces floating on the surface of the water, which are then collected for examination. He is one of the elite team of detection dogs used by scientists studying a number of species including right whales and killer whales.Conservation canines are fast becoming indispensable tools for biologists according to Aimee Hurt, associate director and co-founder of Working Dogs for Conservation, based in Three Forks, Montana.Over the last few years, though, so many new conservation dog projects have sprung up that Hurt can no longer keep track of them all. Her organization’s dogs and their handlers are fully booked to assist field researchers into 2012.“Dogs have such a phenomenal sense of smell”, explained Sam Wasser, director of the Center for Conservation biology at the University of Washington in Seattle. He has worked with scat-detection dogs since 199(g). Scientists have been using Conservation Canines in their research since 199(g). These dogs have enabled them to non-invasively access vast amount of genetic and physiological information which is used to tackle conservation problems around the world. Such information has proved vital for determining the causes and consequences of human disturbances on wildlife as well as the actions needed to mitigate such impacts.The ideal detection dog is extremely energetic with an excessive play drive. These dogs will happily work all • day long, motivated by the expectation of a ball game as a reward for sample detection. The obsessive, high energy personalities of detection dogs also make them difficult to maintain as pets. As a result, they frequently find themselves abandoned to animal shelters, facing euthanasia. The programme rescues these dogs and offers them a satisfying career in conservation research."
# keywords,summary= final_keywords(text,1)
#
# print(keywords)
# print(summary)