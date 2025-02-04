import numpy as np
import re
import os
import pandas as pd
import sys
import pickle
import tensorflow as tf
from ReadData import read_data_as_img, read_data_structured, read_data_st, seq_to_array, seq_to_onehot_array
from Results import report_results_imagedata, make_spider_by_temp, report_results_st, test_results, plot_train_history
from datetime import datetime
from contextlib import redirect_stdout
from keras_self_attention import SeqSelfAttention
import keras
from keras.models import Sequential, Model
from keras.layers import Bidirectional, LSTM, Dropout, Flatten, Dense, Conv2D, MaxPooling2D, Conv1D, concatenate, GlobalAveragePooling1D
from keras.callbacks import EarlyStopping, ReduceLROnPlateau



def lstmattxtisrover3():
        
    seq_input = keras.layers.Input(shape=(200,4))
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(units=64, return_sequences=True, dropout=0.3, input_shape=(200,4)))(seq_input)
    x = tf.keras.layers.Attention()([x, x])
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(units=64, return_sequences=True, dropout=0.3))(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    seq_output = tf.keras.layers.Flatten()(x)
    #x = keras.layers.Dense(1)(x)
    #seq_output = keras.layers.Activation('sigmoid')(x)


    cnn_input = keras.layers.Input(shape=(28,200, 1))
    x = tf.keras.layers.Conv2D(filters=50, kernel_size=(2, 2), activation='relu')(cnn_input)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Conv2D(filters=62, kernel_size=(2, 2), activation='relu')(x)
    x = tf.keras.layers.MaxPooling2D((2,2))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Conv2D(filters=75, kernel_size=(2, 2), activation='relu')(x)
    x = tf.keras.layers.MaxPooling2D((2,2))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Conv2D(filters=87, kernel_size=(2, 2), activation='relu')(x)
    x = tf.keras.layers.MaxPooling2D((2,2))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    #x = tf.keras.layers.Conv1D(filters=100, kernel_size=2, activation='relu')(x)
    #x = tf.keras.layers.MaxPooling2D((2,2))(x)
    #x = tf.keras.layers.Dropout(0.2)(x)
    #x = tf.keras.layers.Flatten()(x)
    #x = tf.keras.layers.Dense(128, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    cnn_output = tf.keras.layers.Flatten()(x)
    
    merged = concatenate([seq_output, cnn_output])
    z = Dense(128, activation="relu")(merged)
    z = Dense(1, activation="sigmoid")(merged)

    model = Model(inputs=[seq_input, cnn_input], outputs=z)

    model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy', "AUC"])

    return model

if __name__ == "__main__":
    seed = 42
    np.random.seed(seed)

    X_train_file = open('../data/serialized/X_train_channels_onehot_noAA.pkl', 'rb')
    y_train_file = open('../data/serialized/y_train_channels_onehot_noAA.pkl', 'rb')
    X_val_file = open('../data/serialized/X_val_channels_onehot_noAA.pkl', 'rb')
    y_val_file = open('../data/serialized/y_val_channels_onehot_noAA.pkl', 'rb')
    X_test_file = open('../data/serialized/X_test_channels_onehot_noAA.pkl', 'rb')
    y_test_file = open('../data/serialized/y_test_channels_onehot_noAA.pkl', 'rb')

    X_train = pickle.load(X_train_file)
    y_train = pickle.load(y_train_file)
    X_val = pickle.load(X_val_file)
    y_val = pickle.load(y_val_file)
    X_test = pickle.load(X_test_file)
    y_test = pickle.load(y_test_file)

    X_train_file.close()
    y_train_file.close()
    X_val_file.close()
    y_val_file.close()
    X_test_file.close()
    y_test_file.close()

    X_train_seq = X_train[:,0,:,5:9]
    print(X_train_seq.shape)
    X_train_cnn = X_train[:,:,:,0]
    print(X_train_cnn.shape)
    X_val_seq = X_val[:,0,:,5:9]
    print(X_val_seq.shape)
    X_val_cnn = X_val[:,:,:,0]
    print(X_val_cnn.shape)
    X_test_seq = X_test[:,0,:,5:9]
    print(X_test_seq.shape)
    X_test_cnn = X_test[:,:,:,0]
    print(X_test_cnn.shape)

    if len(sys.argv) < 2:
        run_id = str(datetime.now()).replace(" ", "_").replace("-", "_").replace(":", "_").split(".")[0]
    else:
        run_id = sys.argv[1]
        #run_id = "".join(categories)

    log_file = "logs/"+run_id+".log"
    hist_file = "logs/"+run_id+".pkl"
    plot_file = "logs/"+run_id+".png"

    model = lstmattxtisrover3()
    model.build([X_train_seq.shape, X_train_cnn.shape])
    
    model.summary()
    with open(log_file, 'w') as f:
        with redirect_stdout(f):
            
            #for layer in model.layers:
            #    print(layer.get_config())
            early_stopping_monitor = EarlyStopping( monitor='val_loss', min_delta=0, patience=10, 
                                                    verbose=1, mode='min', baseline=None,
                                                    restore_best_weights=True)
            reduce_lr_loss = ReduceLROnPlateau(monitor='val_auc', factor=0.5, patience=3, verbose=1, min_delta=1e-4, mode='max')

            history = model.fit([X_train_seq, X_train_cnn], y_train,
                                shuffle=True,
                                batch_size=32,
                                epochs=100,
                                verbose=True,
                                validation_data=([X_val_seq, X_val_cnn], y_val),
                                callbacks=[early_stopping_monitor, reduce_lr_loss])
            print("Train results:\n")
            test_results([X_train_seq, X_train_cnn], y_train, model)
            print("Val results:\n")
            test_results([X_val_seq, X_val_cnn], y_val, model)
            print("Test results:\n")
            test_results([X_test_seq, X_test_cnn], y_test, model)
            

    with open(hist_file, 'wb') as file_pi:
        pickle.dump(history.history, file_pi)

    plot_train_history(history.history, plot_file)