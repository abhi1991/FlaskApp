#!usr/bin/python
import time
start_time = time.time()
import sys
import csv
import numpy
from nltk.cluster import KMeansClusterer, GAAClusterer, euclidean_distance
#import nltk.corpus
from nltk import decorators
import nltk.stem
import uuid
from nltk.stem.snowball import SnowballStemmer

def grouper(filename):
    stemmer_func = nltk.stem.snowball.EnglishStemmer().stem

    @decorators.memoize
    def normalize_word(word):
        return stemmer_func(word.lower())

    def get_words(titles):
        words = set()
        for title in job_titles:
            for word in title.split():
                words.add(normalize_word(word))
        return list(words)

    @decorators.memoize
    def vectorspaced(title):
        title_components = [normalize_word(word) for word in title.split()]
        return numpy.array([
            word in title_components for word in words], numpy.short)
        
    with open(filename) as title_file:

        job_titles = [line.decode('utf-8').strip() for line in title_file.readlines()]
        #name = Data(keyword = job_titles)
        #db.session.add(name)
        #db.session.commit()
        words = get_words(job_titles)
        if len(words) >= 1500:
            k = 75
        elif len(words) >= 500 and len(words) < 1000:
            k = 55
        elif len(words) >200 and len(words)<500:
            k =30
        else:
            k = 15
       

        cluster = KMeansClusterer(k,euclidean_distance,avoid_empty_clusters = True )
        cluster.cluster([vectorspaced(title) for title in job_titles if title])

        classified_examples = [
                cluster.classify(vectorspaced(title)) for title in job_titles
            ]
        global gen_file
        gen_file =str(uuid.uuid4())+".csv"
        f = open("/home/ubuntu/downloads/"+gen_file,'wb')
        try:
            w = csv.writer(f)
            w.writerow(('Search Terms','GroupID'))
            for cluster_id, title in sorted(zip(classified_examples, job_titles)):
                w.writerow((title.encode('utf-8'),cluster_id))
            #print "done"
        finally:
            f.close()
        f1 = open("/home/ubuntu/time/"+gen_file+".txt", 'wb')
        try:
            t = (time.time() - start_time)
            f1.write(str(t))
        finally:
            f.close()
        
        
