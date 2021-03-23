import glob
import json
from bs4 import BeautifulSoup
import ctoken
from nltk import *
import math
import timeit
import shutil

#DECIDE WHAT NON ALPHANUMERIC CHARACTERS TO KEEP

DEFAULT_PATH = 'DEV'
#DEFAULT_JSON_PATH = "Logs/url_token_freq.json"
DEFAULT_URL_PATH = "Logs/url_index.txt"
DEFAULT_INDEXER_PATH = "Logs/indexer.txt"
DEFAULT_MERGE_PATH = "Logs/to_be_merged.txt"
MAX_INDEX_SIZE = 18464
IMPORTANT_MULTIPLEXER = 5
CHAMPIONS_LIMIT = 50

#Documents count (55393) divided by 3: 18464

# if any(char.isalpha() or char.isdigit() for char in stemmer.stem(word))


def write_to_disk_and_sort(partial_index,
                           partial_url,
                           numdocs,
                           json_path=DEFAULT_INDEXER_PATH,
                           url_path=DEFAULT_URL_PATH,
                           merge_path=DEFAULT_MERGE_PATH):

    if partial_index:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as fileiter:
                for posting in fileiter:
                    print(posting)
                    curr_posting = eval(posting.strip('\n'))
                    if curr_posting['term'] in partial_index.keys():
                        curr_posting['index'] += partial_index[curr_posting['term']]
                        curr_posting['index'] = sorted(curr_posting['index'],
                                                 key=lambda token: token['score'],
                                                 reverse=True)
                    with open(merge_path, 'a', encoding='utf-8') as mergefileiter:
                        mergefileiter.write(f'{curr_posting}\n')
            shutil.move(merge_path, json_path)

        else:
            with open(json_path, 'a', encoding='utf-8') as fileiter:
                for term in partial_index:
                    if re.search('[a-zA-Z0-9]', term):
                        fileiter.write(f'{{"term":\"{term}\","index":{partial_index[term]}}}\n')


    # Records url for docid and places it in json file
    with open(url_path, 'a', encoding='utf-8') as fileiter:
        for doc_id in partial_url:
            fileiter.write(f'{{\"doc_id\":\"{doc_id}\",\"url\":\"{partial_url[doc_id]}\"}}\n')

    #Updates scores with document number and sorts
    if numdocs != 0:
        with open(json_path, 'r', encoding='utf-8') as fileiter:
            for posting in fileiter:
                print("Finale", posting)
                curr_posting = eval(posting.strip('\n'))
                for doc in curr_posting['index']:
                    if not doc['important']:
                        doc['score'] *= \
                            math.log(numdocs / len(curr_posting['index']), 10)
                    else:
                        doc['score'] *= \
                            math.log(numdocs / len(curr_posting['index']), 10) * \
                            IMPORTANT_MULTIPLEXER
                curr_posting['index'] = sorted(curr_posting['index'],
                                         key=lambda token: token['score'],
                                         reverse=True)
                #Records only at most the top 50 documents
                if len(curr_posting['index']) > CHAMPIONS_LIMIT:
                    curr_posting['index'] = curr_posting['index'][0:CHAMPIONS_LIMIT]
                with open(merge_path, 'a', encoding='utf-8') as mergefileiter:
                    mergefileiter.write(f'{curr_posting}\n')
        shutil.move(merge_path, json_path)


def create_index(path=DEFAULT_PATH):
    calls_to_merge = 0
    partial_count = 0
    doc_id = 0
    partial_index = {}
    partial_url = {}
    for subdir in glob.glob(os.path.join(path, '*')):
        for filename in glob.glob(os.path.join(subdir, '*.json')):
            with open(filename, encoding='utf-8', mode='r') \
                    as currentFile:
                json_dict = json.load(currentFile)

            #To make sure we haven't stopped
            print(json_dict['url'])

            partial_count += 1

            stemmer = PorterStemmer()
            important_list = []
            soup = BeautifulSoup(json_dict['content'],
                                 features="lxml")
            token_list = [stemmer.stem(word) for word in
                          ctoken.tokenize_page(soup.text)]
            word_freqs = ctoken.computeWordFrequencies(token_list)

            #Computes all important words
            for line in soup.find_all('b'):
                important_list.extend([stemmer.stem(word) for word
                                       in ctoken.tokenize_line(
                        line.get_text())])
            for line in soup.find_all('strong'):
                important_list.extend([stemmer.stem(word) for word
                                       in ctoken.tokenize_line(
                        line.get_text())])
            for line in soup.find_all('h1'):
                important_list.extend([stemmer.stem(word) for word
                                       in ctoken.tokenize_line(
                        line.get_text())])
            for line in soup.find_all('h2'):
                important_list.extend([stemmer.stem(word) for word
                                       in ctoken.tokenize_line(
                        line.get_text())])
            for line in soup.find_all('h3'):
                important_list.extend([stemmer.stem(word) for word
                                       in ctoken.tokenize_line(
                        line.get_text())])

            important_freq = ctoken.computeWordFrequencies(important_list)

            for term in important_freq:
                if term in word_freqs.keys():
                    if word_freqs[term] - important_freq[term] == 0:
                        del word_freqs[term]
                    elif word_freqs[term] - important_freq[term] < 0:
                        important_freq[term] = word_freqs[term]
                        del word_freqs[term]
                    else:
                        word_freqs[term] = \
                            word_freqs[term] - important_freq[term]

            for term in word_freqs:
                score = 1 + math.log(word_freqs[term], 10)
                if term in partial_index.keys():
                    partial_index[term].append(
                        {'doc_id': doc_id, 'score': score, 'important': False})
                else:
                    partial_index[term] = \
                        [{'doc_id': doc_id, 'score': score, 'important': False}]
            for term in important_freq:
                score = 1 + math.log(important_freq[term], 10)
                if term in partial_index.keys():
                    partial_index[term].append(
                        {'doc_id': doc_id, 'score': score, 'important': True})
                else:
                    partial_index[term] = \
                        [{'doc_id': doc_id, 'score': score, 'important': True}]

            partial_url[doc_id] = json_dict['url']
            doc_id += 1

            #Merges if partial list hits certain threshold
            if partial_count == MAX_INDEX_SIZE:
                calls_to_merge += 1
                write_to_disk_and_sort(partial_index, partial_url, 0)
                partial_count = 0
                partial_index = {}
                partial_url = {}

    #Final Merge, now with all the doc counts
    write_to_disk_and_sort(partial_index, partial_url, doc_id+1)
    return calls_to_merge


if __name__ == '__main__':
    start = timeit.default_timer()
    print("Calls to merge:", create_index())
    stop = timeit.default_timer()
    print(f'Time to run: {stop - start}')





