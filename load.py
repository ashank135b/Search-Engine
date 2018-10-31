import pickle
import json
import nltk
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from Trie import Trie

stemmer = SnowballStemmer(language="english", ignore_stopwords=True)

terms = []
trie = Trie()
all_words = []

def load():
    """
    Calculated TF-IDF ranking of the dataset
    """
    f = open("booksummaries/booksummaries.txt", encoding="utf8")
    s = f.read()
    data = {}
    docs = 1000

    global terms
    global trie
    global all_words

    text = s.split("\t")

    # tf
    for i in range(docs):
        print(i)
        s = text[6 * i + 6]
        tokens = nltk.word_tokenize(s)
        for token in tokens:
            trie.insert(token)
            all_words.append(token)
        tokens = [stemmer.stem(token.lower()) for token in tokens if token.isalnum()]
        N = len(tokens)
        d = {token: tokens.count(token) / float(N) for token in tokens}
        terms = terms + (list(d.keys()))
        terms = list(set(terms))
        try:
            genre = json.loads(text[6 * i + 5])
        except Exception:
            genre = {}
        data[text[6 * i + 2]] = {'author': text[6 * i + 3], 'genre': genre, 'tf': d, 'date': text[6 * i + 4],
                                 'index': i}

    # idf
    idf = {}

    for term in terms:
        idf[term] = 0
        for story in data.keys():
            if term in data[story]['tf'].keys():
                idf[term] += 1
        try:
            idf[term] = np.log10(float(docs) / idf[term] + 1)
        except:
            idf[term] = 0

    # score
    for story in data.keys():
        tf = data[story]['tf']
        vec = {}
        for key in idf.keys():
            if key in tf.keys():
                vec[key] = idf[key] * tf[key]
            else:
                vec[key] = 0
        data[story]['tf'] = vec

    with open("storevec.txt", "wb") as file:
        pickle.dump(data, file)
    with open("storeidf.txt", "wb") as file:
        pickle.dump(idf, file)
    with open("storedata.txt", "wb") as file:
        pickle.dump(text, file)


load()

new = all_words

all_words = set(all_words)
all_words = sorted(all_words)
print(all_words)

with open("storewords.txt", "wb") as file:
    pickle.dump(all_words, file)

with open("storetrie.txt", "wb") as file:
    pickle.dump(trie, file)