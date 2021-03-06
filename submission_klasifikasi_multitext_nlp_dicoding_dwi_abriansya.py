# -*- coding: utf-8 -*-
"""Submission Klasifikasi Multitext NLP Dicoding - Dwi Abriansya.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15sFMY_2wjwMLVO3UTxkwETPLd_ofbXAJ

Nama              : Dwi Abriansya Alimuddin

No Registrasi FGA : 0182180121-127

# Submission Klasifikasi Multitext NLP Dicoding

## Upload dan Read Dataset
"""

# Upload File Dataset
from google.colab import files
uploaded = files.upload()

# Read File Dataset
import pandas as pd
train = pd.read_csv('train.txt', sep=';', names=['sentences', 'feelings'])
test = pd.read_csv('test.txt', sep=';', names=['sentences', 'feelings'])
val = pd.read_csv('val.txt', sep=';', names=['sentences', 'feelings'])

df = train.append(test)
df = df.append(val)
df.head()

"""## Data Preprocessing

### Null dan Duplicated Data
"""

df.info()

# Cek Data Null
df.isna().sum()

# Cek Data Duplicated
df.duplicated().sum()

# Hilangkan Duplicated Data
df.drop_duplicates(inplace=True)

"""### Feature Engineering"""

# One-Hot Encoding Label
category = pd.get_dummies(df['feelings'])
df_baru = pd.concat([df, category], axis=1)
df_baru = df_baru.drop(columns='feelings')
df_baru

"""## Train Test Split"""

sinopsis = df_baru['sentences'].values
label = df_baru[['anger', 'fear', 'joy', 'love', 'sadness', 'surprise']].values

# Train Test Split dengan Rasio Train 80% dan Test 20%
from sklearn.model_selection import train_test_split
sinopsis_latih, sinopsis_test, label_latih, label_test = train_test_split(sinopsis, label, test_size=0.2)

"""## Mencari Banyak Kata"""

# Inisiasi Fungsi Hitung Kata
from collections import Counter

def counter_words(text):
  count = Counter()
  for i in text.values:
    for word in i.split():
      count[word] += 1
  return count

# Menghitung Banyak Kata
sentence = df_baru['sentences']
counter = counter_words(sentence)
num_words = len(counter)
num_words

"""## Tokenizer"""

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
 
tokenizer = Tokenizer(num_words=num_words, oov_token='x')
tokenizer.fit_on_texts(sinopsis_latih) 
tokenizer.fit_on_texts(sinopsis_test)
 
sekuens_latih = tokenizer.texts_to_sequences(sinopsis_latih)
sekuens_test = tokenizer.texts_to_sequences(sinopsis_test)
 
padded_latih = pad_sequences(sekuens_latih) 
padded_test = pad_sequences(sekuens_test)

"""## Arsitektur Model"""

import tensorflow as tf

model = tf.keras.Sequential([
    # Embedding dengan dimensi input sebanyak kata dan dimensi output 64
    tf.keras.layers.Embedding(input_dim=num_words, output_dim=64),
    # LSTM dengan output 128 neuron
    tf.keras.layers.LSTM(128),        
    # Hidden layer dengan 64 neuron               
    tf.keras.layers.Dense(64, activation='relu'),
    # Dropout layer 0.5
    tf.keras.layers.Dropout(0.5),
    # Output layer, klasifikasi 6 class sehingga menggunakan aktivasi softmax
    tf.keras.layers.Dense(6, activation='softmax')])

model.compile(
    loss='categorical_crossentropy',
    optimizer='rmsprop',
    metrics=['accuracy'])

"""### Inisiasi Fungsi Callback"""

# Inisiasi fungsi callback dengan syarat akurasi 90%
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get('val_accuracy')>0.90) & (logs.get('accuracy')>0.90):
      print('\nAkurasi telah mencapai >90%!')
      self.model.stop_training = True

# Inisiasi class myCallback ke dalam variable callbacks
callbacks = myCallback()

"""## Training Model"""

# Training model
history = model.fit(
    padded_latih, label_latih,                  # Data Train
    epochs=30,                                  # Jumlah Epoch
    validation_data=(padded_test, label_test),  # Data Test
    callbacks=callbacks,                        # Memanggil Fungsi Callbacks
    verbose=1)                                  # Menampilkan Hasil Epoch

"""## Plot Loss dan Accuracy"""

import matplotlib.pyplot as plt

# Ekstrak akurasi dan loss dari training model
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

# Plot akurasi training dan validasi
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()

# Plot loss training dan validasi
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()

plt.show()