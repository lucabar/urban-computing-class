import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
from datetime import datetime


folders_clean = np.load("arrays/clean_folders.npy")

input_clean = np.load("arrays/clean_input.npy")
input_clean = input_clean.reshape(len(input_clean),120,120,3)
input_shape = input_clean.shape

labels_clean = np.load("arrays/clean_labels.npy")
labels_categorical = tf.keras.utils.to_categorical(labels_clean, num_classes=10)
print("Arrays have been loaded...")

test_split = True
if test_split:
    input_train, input_test, labels_train, labels_test = train_test_split(
        input_clean, labels_categorical, test_size=0.2, random_state=42
    )

    input_train = tf.convert_to_tensor(input_train, dtype=tf.float32)
    labels_train = tf.convert_to_tensor(labels_train, dtype=tf.float32)
    input_test = tf.convert_to_tensor(input_test, dtype=tf.float32)
    labels_test = tf.convert_to_tensor(labels_test, dtype=tf.float32)

print("Train test split successful...")

# same structure network but not pre-trained (initialised): init
input_t = tf.keras.Input(shape=(120,120,3))
model_res = tf.keras.applications.resnet50.ResNet50(
    include_top=False,
    weights=None,
    input_tensor=input_t,
    input_shape=(120,120,3),
    pooling=None,
    classes=10,
)

# pretrained model
model = tf.keras.Sequential()
model.add(model_res)
model.add(layers.Flatten())
model.add(layers.BatchNormalization())
model.add(layers.Dense(32, activation="relu"))
model.add(layers.Dropout(0.5))
model.add(layers.BatchNormalization())
model.add(layers.Dense(10, activation="softmax"))
model.summary()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"init_network at {timestamp}.")
log_dir = f"logs/init_{timestamp}/"
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1,update_freq='batch')

checkpoint_path = f"weights/init_{timestamp}.h5"

model_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, save_best_only=True, save_weights_only=True)

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

history = model.fit(
    input_train, labels_train,
    epochs=5, batch_size=32, verbose=1,
    validation_split=0.2,
    callbacks=[tensorboard_callback, model_callback]
)

# Evaluate the model on the test data
test_loss, test_accuracy = model.evaluate(input_test, labels_test, verbose=2)
print(f"\nTest Accuracy: {test_accuracy * 100:.2f}%")

predictions = model.predict(input_clean)
predicted_labels = np.argmax(predictions, axis=1)
true_labels = np.argmax(labels_clean, axis=1)


precision = precision_score(true_labels, predicted_labels, average='weighted')
recall = recall_score(true_labels, predicted_labels, average='weighted')
f1 = f1_score(true_labels, predicted_labels, average='weighted')
print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}")
