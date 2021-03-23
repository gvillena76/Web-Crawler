Intro
==
This is Gabriel Villena's Search Engine.
The way it works is as follows:

There are 3 python files: 

indexer_utils - Creates the inverted index and URL index

ctoken - tokenizer from assignment 2

query - takes the input and computes the results

The Indexer
===
The function parses through the web pages and loads them into
a dict.  The content value is tokenized and returned as
computed frequenices.  The program runs through the page again
looking for important tags.  Each frequency is placed into a
posting structure made out of a dictionary.  These dictionary
is placed in a list based on its associated term.  Once the
partial limit is reached, the program enters a write-to-disk
function where it reads the old indexer txt file and compares
it to the partial list.  Each term checks if it's in the partial
index and if so, it adds on to the partial index.  The partial
list is then written onto the merged txt file, containing both
the partial index and the old file.  The merged file overrwrites
the old file.  At the end, the file is iterated and merged again,
this time mutiplying by the idf.  Each partial index goes has
their url checked to be added onto the url_index.  Each time a
partial index is passed into the write-to-disk function, the
posting lists get sorted by tf-idf score, which is computed
after the final webpageis parsed.  After this, the merged index
takes in champion lists of 50 of the highest scoring documents.

The Query
===
The query takes in the indexer and url index and reads through
them.  The user inputs a request and that request gets tokenized.
For each token, we find the associated posting list.  Since the
lists are sorted by score, we grab only the first few postings.
The posting doc-ids are passed to use as an index finder for
the url_index txt file, where it matches up the doc_id with the
url.


