import numpy as np
import os
import PIL
import PIL.Image
import tensorflow as tf

from tensorflow.keras.preprocessing import image_dataset_from_directory

#print(tf.__version__)
!pip install -q -U watermark

# Commented out IPython magic to ensure Python compatibility.
# %reload_ext watermark
# %watermark -v -p numpy,pandas,tensorflow,PIL

import pathlib

data_dir = pathlib.Path('drive/My Drive/Dataset/DatasetBruna')
# train_dir = os.path.join(data_dir, 'Data')
# validation_dir = os.path.join(data_dir, 'Data')

image_count = len(list(data_dir.glob('*/*')))
print(image_count)

list_ds = tf.data.Dataset.list_files(str(data_dir/'*/*'), shuffle=False)
list_ds = list_ds.shuffle(image_count, reshuffle_each_iteration=False)

for f in list_ds.take(5):
   print(f.numpy())

class_names = np.array(sorted([item.name for item in data_dir.glob('*') if item.name != "LICENSE.txt"]))
print(class_names)

import numpy as np
from matplotlib import pyplot as plt

val_size = int(image_count * 0.2)
train_ds = list_ds.skip(val_size)
val_ds = list_ds.take(val_size)

print(tf.data.experimental.cardinality(train_ds).numpy())
print(tf.data.experimental.cardinality(val_ds).numpy())

def get_label(file_path):
  #convert the path to a list of path components
  parts = tf.strings.split(file_path, os.path.sep)
  # The second to last is the class-directory
  one_hot = parts[-2] == class_names
  # Integer encode the label
  return tf.argmax(one_hot)

def decode_img(img):
  # convert the compressed string to a 3D uint8 tensor
  img = tf.image.decode_jpeg(img, channels=3)
  # resize the image to the desired size
  return tf.image.resize(img, [img_height, img_width])

def process_path(file_path):
  label = get_label(file_path)
  # load the raw data from the file as a string
  img = tf.io.read_file(file_path)
  img = decode_img(img)
  return img, label

AUTOTUNE = tf.data.experimental.AUTOTUNE

train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

batch_size = 9
img_height = 400    
img_width = 600

# Set `num_parallel_calls` so multiple images are loaded/processed in parallel.
train_ds = train_ds.map(process_path, num_parallel_calls=AUTOTUNE)
val_ds = val_ds.map(process_path, num_parallel_calls=AUTOTUNE)

for image, label in train_ds.take(1):
  print("Image shape: ", image.numpy().shape)
  print("Label: ", label.numpy())

def configure_for_performance(ds):
  ds = ds.cache()
  ds = ds.shuffle(buffer_size=1000)
  ds = ds.batch(batch_size)
  ds = ds.prefetch(buffer_size=AUTOTUNE)
  return ds

train_ds = configure_for_performance(train_ds)
val_ds = configure_for_performance(val_ds)

from numpy import expand_dims
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot

image.shape

from tensorflow.keras import layers

normalization_layer = tf.keras.layers.experimental.preprocessing.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixels values are now in `[0,1]`.
print(np.min(first_image), np.max(first_image))

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten

#val_ds[1]

"""##RESNET50##"""

# load model and specify a new input shape for images and avg pooling output
new_input = tf.keras.layers.Input(shape=(400, 600, 3))

# load model without classifier layers
model1 = tf.keras.applications.ResNet50(include_top=False, input_tensor=new_input, weights='imagenet')
model1.trainable = True
# add new classifier layers
flat1 = Flatten()(model1.layers[-1].output)
class1 = Dense(128, activation='relu')(flat1)
output = Dense(3, activation='softmax')(class1)
# define new model
model1 = Model(inputs=model1.inputs, outputs=output)
# summarize
model1.summary()

base_learning_rate = 0.001
model1.compile(optimizer=tf.keras.optimizers.SGD(lr=base_learning_rate),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history1 = model1.fit(train_ds,
                    validation_data=(val_ds),  
                    epochs=50)

"""##XCEPTION##"""

# load model and specify a new input shape for images and avg pooling output
new_input = tf.keras.layers.Input(shape=(400, 600, 3))

# load model without classifier layers
model2 = tf.keras.applications.Xception(include_top=False, input_tensor=new_input, weights='imagenet')
model2.trainable = True
# add new classifier layers
flat1 = Flatten()(model2.layers[-1].output)
class1 = Dense(128, activation='relu')(flat1)
output = Dense(3, activation='softmax')(class1)
# define new model
model2 = Model(inputs=model2.inputs, outputs=output)
# summarize
model2.summary()

base_learning_rate = 0.001
model2.compile(optimizer=tf.keras.optimizers.SGD(lr=base_learning_rate),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history2 = model2.fit(train_ds,
                    validation_data=(val_ds),  
                    epochs=50)

import numpy as np
import pathlib

data_dir = pathlib.Path('drive/My Drive/Dataset/DatasetBruna')
class_names = np.array(sorted([item.name for item in data_dir.glob('*') if item.name != "LICENSE.txt"]))
print(class_names)

labels = '\n'.join(class_names)

with open('labels.txt', 'w') as f:
  f.write(labels)

import tensorflow as tf
saved_model_dir = 'drive/My Drive/Dataset/'
tf.saved_model.save(model2, saved_model_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
tflite_model = converter.convert()

with open('model2.tflite', 'wb') as f:
  f.write(tflite_model)

from google.colab import files

files.download('model2.tflite')
files.download('labels.txt')

"""##MOBILE NET##"""

# load model and specify a new input shape for images and avg pooling output
new_input = tf.keras.layers.Input(shape=(400, 600, 3))

# load model without classifier layers
model3 = tf.keras.applications.MobileNet(include_top=False, input_tensor=new_input, weights='imagenet')
model3.trainable = True
# add new classifier layers
flat1 = Flatten()(model3.layers[-1].output)
class1 = Dense(128, activation='relu')(flat1)
output = Dense(3, activation='softmax')(class1)
# define new model
model3 = Model(inputs=model3.inputs, outputs=output)
# summarize
model3.summary()

base_learning_rate = 0.001
model3.compile(optimizer=tf.keras.optimizers.SGD(lr=base_learning_rate),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history3 = model3.fit(train_ds,
                    validation_data=(val_ds),  
                    epochs=50)

"""##INCEPTIONV3##"""

# load model and specify a new input shape for images and avg pooling output
new_input = tf.keras.layers.Input(shape=(400, 600, 3))

# load model without classifier layers
model4 = tf.keras.applications.InceptionV3(include_top=False, input_tensor=new_input, weights='imagenet')
model4.trainable = True
# add new classifier layers
flat1 = Flatten()(model4.layers[-1].output)
class1 = Dense(128, activation='relu')(flat1)
output = Dense(3, activation='softmax')(class1)
# define new model
model4 = Model(inputs=model4.inputs, outputs=output)
# summarize
model4.summary()

base_learning_rate = 0.001
model4.compile(optimizer=tf.keras.optimizers.SGD(lr=base_learning_rate),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history4 = model4.fit(train_ds,
                    validation_data=(val_ds),  
                    epochs=50)

"""##MEU MODELO##"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow import keras

num_classes = 3

  #_______________________ Parte Convolucional
model5 = tf.keras.Sequential([
     keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(400,600,3)),
     keras.layers.MaxPooling2D((2,2)),
     keras.layers.Conv2D(64, (3,3), activation='relu'),
     keras.layers.MaxPooling2D((2,2)),
     keras.layers.Conv2D(128, (3,3), activation='relu'),
     keras.layers.MaxPooling2D((2,2)),
     keras.layers.Conv2D(128, (3,3), activation='relu'),
     keras.layers.MaxPooling2D((2,2)),

  #_______________________ Rede Neural

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(3, activation='softmax')])
    #keras.layers.Flatten(),
    #keras.layers.Dense(128, activation='relu'),
    #keras.layers.Dense(num_classes, activation='softmax')])

  #_______________________ summarize
model5.summary()

base_learning_rate = 0.001
model5.compile(optimizer=tf.keras.optimizers.Adam(lr=base_learning_rate),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history5 = model5.fit(train_ds,
                    validation_data=(val_ds),  
                    epochs=50)

import tensorflow as tf
saved_model_dir = 'drive/My Drive/Dataset/'
tf.saved_model.save(model5, saved_model_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
tflite_model = converter.convert()

with open('model5.tflite', 'wb') as f:
  f.write(tflite_model)

from google.colab import files

files.download('model5.tflite')
files.download('labels.txt')

"""**GR??FICOS**"""

plt.plot(history1.history['val_loss'])
plt.plot(history2.history['val_loss'])
plt.plot(history3.history['val_loss'])
plt.plot(history4.history['val_loss'])
plt.plot(history5.history['val_loss'])
plt.title('Validation loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['ResNet50', 'Xception', 'MobileNet', 'InceptionV3', 'Meu modelo'], loc='upper right')
plt.show()

plt.plot(history1.history['loss'])
plt.plot(history2.history['loss'])
plt.plot(history3.history['loss'])
plt.plot(history4.history['loss'])
plt.plot(history5.history['loss'])
plt.title('Train loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['ResNet50', 'Xception', 'MobileNet', 'InceptionV3', 'Meu modelo'], loc='upper right')
plt.show()

# ver val_ds para conferir labels
plt.plot(history1.history['val_accuracy'])
plt.plot(history2.history['val_accuracy'])
plt.plot(history3.history['val_accuracy'])
plt.plot(history4.history['val_accuracy'])
plt.plot(history5.history['val_accuracy'])
plt.title('Validation accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['ResNet50', 'Xception', 'MobileNet', 'InceptionV3', 'Meu modelo'], loc='lower right')
plt.show()

# ver val_ds para conferir labels
plt.plot(history1.history['accuracy'])
plt.plot(history2.history['accuracy'])
plt.plot(history3.history['accuracy'])
plt.plot(history4.history['accuracy'])
plt.plot(history5.history['accuracy'])
plt.title('Train accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['ResNet50', 'Xception', 'MobileNet', 'InceptionV3', 'Meu modelo'], loc='lower right')
plt.show()

"""##**Predi????es**##"""

list_val = list(val_ds)

y = np.concatenate([y for x, y in list_val])
x = np.concatenate([x for x, y in list_val])

predictions = model5.predict(x)

predictions[1]

y_pred = np.argmax(predictions, axis=1)

"""**Matriz de confus??o**"""

from sklearn.metrics import confusion_matrix

CM = confusion_matrix(y, y_pred)
print(CM)
print('\nTeste Accuracy: ' + str(np.sum(np.diag(CM)) / np.sum(CM)))

import seaborn
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

fig_dims = (15,10)
fig, ax = plt.subplots(figsize=fig_dims)
sns.heatmap(CM/np.sum(CM), annot=True, 
            fmt='.2%', xticklabels=class_names, yticklabels=class_names, cmap='Blues')

#seaborn.heatmap(CM, annot=True, ax=ax, fmt='d', xticklabels=class_names, yticklabels=class_names, cmap="YlGnBu")
#plt.show()

x.shape

import time

ti = time.time()

predictions = model5.predict(x)
y_pred = np.argmax(predictions, axis=1)

tf = time.time()
elapsed = tf-ti

elapsed
