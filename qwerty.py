from keras.models import Model
from keras.layers import Flatten, Dense
from keras.applications.vgg16 import VGG16
import matplotlib.pyplot as plt
from glob import glob
import os

# Ensure directories for saving plots and model exist
os.makedirs('plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

IMAGE_SHAPE = [224, 224, 3] # VGG16 architecture's fixed-size
vgg_model = VGG16(input_shape=IMAGE_SHAPE, weights='imagenet', include_top=False)

# Define paths
training_data = 'chest_xray/train'
testing_data = 'chest_xray/test'

# Freeze the layers of VGG16
for layer in vgg_model.layers:
    layer.trainable = False

classes = 2
flatten_layer = Flatten()(vgg_model.output)
prediction = Dense(classes, activation='softmax')(flatten_layer)
final_model = Model(inputs=vgg_model.input, outputs=prediction)
final_model.summary()

# Compile the model
final_model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

from keras.preprocessing.image import ImageDataGenerator

# Data augmentation
train_datagen = ImageDataGenerator(rescale=1./255, shear_range=0.2, zoom_range=0.2, horizontal_flip=True)
test_datagen = ImageDataGenerator(rescale=1./255)

# Load images
training_set = train_datagen.flow_from_directory(
    training_data,
    target_size=(224, 224),
    batch_size=4,
    class_mode='categorical'
)
test_set = test_datagen.flow_from_directory(
    testing_data,
    target_size=(224, 224),
    batch_size=4,
    class_mode='categorical'
)

# Train the model
fitted_model = final_model.fit(
    training_set,
    validation_data=test_set,
    epochs=5,
    steps_per_epoch=len(training_set),
    validation_steps=len(test_set)
)

# Plotting
def plot_metrics(history, metric, filename):
    plt.figure()
    plt.plot(history.history[metric], label=f'training {metric}')
    plt.plot(history.history[f'val_{metric}'], label=f'validation {metric}')
    plt.legend()
    plt.savefig(os.path.join('plots', filename))

plot_metrics(fitted_model, 'loss', 'LossVal_loss.png')
plot_metrics(fitted_model, 'accuracy', 'AccVal_acc.png')

# Save the model
final_model.save(os.path.join('models', 'model_AV.h5'))