import ctoken
from nltk import *
import timeit
import ast
import json

#DEFAULT_PATH = 'DEV'
#DEFAULT_JSON_PATH = "Logs/url_token_freq.json"
DEFAULT_URL_PATH = "Logs/url_index.txt"
DEFAULT_INDEXER_PATH = "Logs/indexer.txt"


def compute_document_scores():

    with open(DEFAULT_URL_PATH, 'rb') as urliter:
        urliter.seek(0)
        url_index = urliter.read().decode(encoding='utf-8')
        urliter.seek(0)

        with open(DEFAULT_INDEXER_PATH, 'rb') as indexiter:
            indexiter.seek(0)
            index = indexiter.read().decode(encoding='utf-8')
            indexiter.seek(0)

            #Take input and stem tokens
            stemmer = PorterStemmer()
            query = [stemmer.stem(word) for
                     word in
                     ctoken.tokenize_line(input("Please enter a query:"))]

            start = timeit.default_timer()
            query_postings = []
            for token in query:
                if index.find(f'{{\'term\': \'{token}\', \'index\':') != -1:
                    indexiter.seek(index.find(f'{{\'term\': \'{token}\', \'index\':'))
                    diction = eval(indexiter.readline().decode(encoding='utf-8').rstrip('\\r\\n').lstrip('\\b'))
                    query_postings.append(diction)
        query_postings = sorted(query_postings, key=lambda x: len(x['index']))
        if len(query_postings) != 0:

            if len(query_postings[0]['index']) < 5:
                results = {posting['doc_id']: posting['score'] for
                           posting in query_postings[0]['index']}
            else:
                results = {posting['doc_id']: posting['score'] for posting in
                           query_postings[0]['index'][0:5]}

            for token in query_postings[1:len(query_postings)-1]:
                doc_match = 0
                for posting in token['index']:
                    if posting['doc_id'] in results.keys():
                        results[posting['doc_id']] += posting['score']
                        doc_match += 1
                    elif len(results) < 5:
                        results[posting['doc_id']] = posting['score']
                        doc_match += 1
                    if doc_match == 5:
                        break

        results = {tuple[0]:tuple[1] for tuple in sorted(results.items(), key=lambda item: item[1], reverse=True)}
        print("=================Top Results===================")
        for result in results:
            urliter.seek(url_index.find(f'{{\"doc_id\":\"{result}\",\"url\":'))
            url = eval(urliter.readline().decode(encoding='utf-8').rstrip('\\r\\n').lstrip('\\b'))
            print(url['url'], 'with a score of', results[result], '')

    stop = timeit.default_timer()
    return stop - start


def intersect(term1, term2):
    answer = []
    term1_ind = 0
    term2_ind = 0
    while term1_ind < len(term1)-1 and term2_ind < len(term2)-1:
        if term1[term1_ind][0] == term2[term2_ind][0]:
            answer.append(term1[term1_ind])
            term1_ind += 1
            term2_ind += 1
        elif int(term1[term1_ind][0]) < int(term2[term2_ind][0]):
            term1_ind += 1
        else:
            term2_ind += 1
    return answer


def test():
    term = "89@88"
    if re.search('[a-zA-Z0-9]', term):
        print("works")
    else:
        print("nope")



if __name__ == '__main__':
    #print('Time to run:', compute_document_scores())
    test()



