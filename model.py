import re 
import nltk
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import neattext.functions as nfx
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from nltk.corpus import stopwords
from keras.preprocessing.text import one_hot
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import OneHotEncoder
from keras.models import Sequential
from keras.layers import Embedding, Dense, LSTM, Dropout
from keras.callbacks import Callback, EarlyStopping
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

train_df = pd.read_csv('data/train.txt',header=None, sep=';', names=['Text','Emotion'])
valid_df = pd.read_csv('data/val.txt',header=None, sep=';', names=['Text','Emotion'])
test_df = pd.read_csv('data/test.txt',header=None, sep=';', names=['Text','Emotion'])

print(train_df.head())

lb = LabelEncoder()
train_df['Label'] = lb.fit_transform(train_df['Emotion'])
valid_df['Label'] = lb.fit_transform(valid_df['Emotion'])
test_df['Label'] = lb.fit_transform(test_df['Emotion'])

vocab_size = 1000
len_sentence=150


from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences

nltk.download('stopwords')
stopwords = set(nltk.corpus.stopwords.words('english'))

def text_prepare(data, column):
    print(data.shape)
    stemmer = PorterStemmer()
    corpus = []
    
    for text in data[column]:
        text = re.sub("[^a-zA-Z]", " ", text)
        
        text = text.lower()
        text = text.split()
        
        text = [stemmer.stem(word) for word in text if word not in stopwords]
        text = " ".join(text)
        
        corpus.append(text)
    one_hot_word = [one_hot(input_text=word, n=vocab_size) for word in corpus]
    embeddec_doc = pad_sequences(sequences=one_hot_word,
                              maxlen=len_sentence,
                              padding="pre")
    print(data.shape)
    return embeddec_doc

X_train=text_prepare(train_df, "Text")
X_valid =text_prepare(valid_df, "Text")
X_test=text_prepare(test_df, "Text")


y_train = train_df['Label']
y_valid = valid_df['Label']
y_test = test_df['Label']

enc = OneHotEncoder()

# y_train
y_train = np.array(y_train)
y_train = enc.fit_transform(y_train.reshape(-1,1)).toarray()

y_test
y_test = np.array(y_test)
y_test = enc.fit_transform(y_test.reshape(-1,1)).toarray()

# y_valid
y_valid = np.array(y_valid)
y_valid = enc.fit_transform(y_valid.reshape(-1,1)).toarray()



model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=150, input_length=len_sentence))
model.add(Dropout(0.2))
model.add(LSTM(200))
model.add(Dropout(0.3))
model.add(Dense(120, activation="relu"))
model.add(Dropout(0.3))
model.add(Dense(6, activation="softmax"))
model.compile(optimizer="Adam", loss = "categorical_crossentropy", metrics=["accuracy"])

hist = model.fit(X_train, y_train, epochs = 100, batch_size = 32, validation_data=(X_valid, y_valid),verbose = 1)

fig, ax = plt.subplots(1, 2, figsize=(10, 3))
ax = ax.ravel()

for i, met in enumerate(['accuracy', 'loss']):
    ax[i].plot(hist.history[met])
    ax[i].plot(hist.history['val_' + met])
    ax[i].set_title('Model {}'.format(met))
    ax[i].set_xlabel('epochs')
    ax[i].set_ylabel(met)
    ax[i].legend(['train', 'val']) 

model.save('model')