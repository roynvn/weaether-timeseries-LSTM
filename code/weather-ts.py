# -*- coding: utf-8 -*-
"""Submission_TS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gkRF7m7QQnKBfQRJRr6DBqzFIS29JzM-

KAGGLE CONF
"""

from google.colab import files
!pip install -q kaggle

#upload api key
uploaded = files.upload()

! mkdir ~/.kaggle/
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

! kaggle datasets download -d jsphyg/weather-dataset-rattle-package
! unzip weather-dataset-rattle-package.zip

#ALL IMPORT 
import pandas as pd 
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.preprocessing.sequence import TimeseriesGenerator
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np

"""DATA USED"""

df = pd.read_csv("weatherAUS.csv")
df = df [:12000]
df

print("DATA YANG DIGUNAKAN: ",len(df))

df.isnull().sum()

#drop kolom yang tidak digunakan
data = df.filter(['Date','MaxTemp'], axis=1)
data

data.isnull().sum()

mean_maxtemp = round(data['MaxTemp'].mean(),1)
#isi yang kosong dengan rata-rata
values = {'MaxTemp':mean_maxtemp}
data = data.fillna(value=values)
data.isnull().sum()

data

#10% dari data
max = df['MaxTemp'].max()
print('Max value: ',max)
min = df['MaxTemp'].min()
print('Min value: ',min)
result = (max-min) * (10/100)
print(result)

dates = data['Date'].values
max_temp = data['MaxTemp'].values

plt.figure(figsize=(15,5))
plt.plot(dates,max_temp)
plt.title("Temperature Average", fontsize=20)

X_train, X_test, y_train, y_test = train_test_split(dates,max_temp, test_size=0.2, shuffle = False )

def windowed_dataset(series, window_size, batch_size,shuffle_buffer):
  series = tf.expand_dims(series,axis=1)
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
  ds = ds.flat_map(lambda w: w.batch(window_size+1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

tf.keras.backend.set_floatx('float64')

train_set = windowed_dataset(y_train, window_size=64, batch_size=200, shuffle_buffer=1000)
test_set = windowed_dataset(y_test, window_size=64, batch_size=200, shuffle_buffer=1000)

model = tf.keras.models.Sequential([
                                   tf.keras.layers.LSTM(60, return_sequences=True),
                                   tf.keras.layers.LSTM(60),
                                   tf.keras.layers.Dense(30, activation='relu'),
                                   tf.keras.layers.Dense(10, activation='relu'),
                                   tf.keras.layers.Dense(1)
                                   
])

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae') < result and logs.get('val_mae') < result):
      print("\nMAE dari model < 10% skala data")
      self.model.stop_training = True
callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(loss= tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=['mae'])
history = model.fit(train_set, 
                    epochs=100,
                    batch_size=64,
                    validation_data = test_set, 
                    callbacks=[callbacks]
                    )

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('MAE')
plt.ylabel('mae')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()

