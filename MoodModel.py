import re
import os
import pandas as pd
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').disabled = True
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from tensorflow import keras
import pickle

nltk.download('punkt')
nltk.download('stopwords')

stopwords = stopwords.words('english')

def lower_text(text):
    return text.lower()

def remove_number(text):
    num = re.compile(r'[-+]?[.\d]*[\d]+[:,.\d]*')
    return num.sub(r'', text)

def remove_punct(text):
    punctuations = '@#!?+&*[]-%.:/();$=><|{}^' + "'`"
    for p in punctuations:
        text = text.replace(p, f' {p} ')
    return text
    
def remove_stopwords(text):
    text = ' '.join([word for word in text.split() if word not in (stopwords)])
    return text
    
def clean_text(text):
    text = lower_text(text)
    text = remove_number(text)
    text = remove_punct(text)
    text = remove_stopwords(text)
    
    return text

train_df = pd.read_csv("data/train.txt", sep=";", header= None, names=["text", "label"])

train_df["clean_text"] = train_df["text"].apply(clean_text)

x_train = train_df["clean_text"]

tokenizer = Tokenizer()
tokenizer.fit_on_texts(x_train)

vocab_size = 15065
maxlen = 35

model = keras.models.load_model('MainModel/model')
model.load_weights('MainModel/model_weights.h5')

model.load_weights('MainModel/model_weights.h5')
def get_feelings(text):
    input_data = pad_sequences(tokenizer.texts_to_sequences([clean_text(text)]), padding='post', maxlen=maxlen)
    answers = ['anger', 'fear', 'joy', 'love', 'sadness', 'surprise']
    
    res = np.argmax(model.predict(input_data))

    return answers[res]
