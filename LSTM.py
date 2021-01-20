import numpy as np
import re
import os
import autokeras as ak
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pickle
import keras
from keras.models import Sequential
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D, AveragePooling2D, LayerNormalization
from keras.layers import Conv3D, MaxPooling3D, AveragePooling3D
from keras.layers import Attention, LSTM
from ReadData import read_data_as_img, read_data_structured, read_data_st, seq_to_array, seq_to_onehot_array
from Preprocessing import ros, smote, adasyn
from Results import report_results_imagedata, make_spider_by_temp, report_results_st, test_results, plot_train_history
from keras import backend as K
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model
from keras import Sequential
from sklearn.metrics import f1_score, roc_auc_score, accuracy_score, log_loss, fowlkes_mallows_score, cohen_kappa_score, precision_score, recall_score
from datetime import datetime
from contextlib import redirect_stdout
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence

def lstm_net():

    model = keras.Sequential()
    #model.add(Embedding(5, 4, input_length=200))
    model.add(LSTM(4))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=["accuracy", "AUC"])

    return model
    

if __name__ == "__main__":
    seed = 42
    np.random.seed(seed)

    X_train_pos = seq_to_onehot_array('../data/prueba/onlyseq.TSSposFineGrained.hg16-train.pos')[0].astype(np.float32)
    X_train_neg = seq_to_onehot_array('../data/prueba/onlyseq.TSSnegFineGrained.hg16-train.neg')[0].astype(np.float32)
    X_val_pos = seq_to_onehot_array('../data/prueba/onlyseq.TSSposFineGrained.hg16-val.pos')[0].astype(np.float32)
    X_val_neg = seq_to_onehot_array('../data/prueba/onlyseq.TSSnegFineGrained.hg16-val.neg')[0].astype(np.float32)
    X_test_pos = seq_to_onehot_array('../data/prueba/onlyseq.TSSposFineGrained.hg17-test.pos')[0].astype(np.float32)
    X_test_neg = seq_to_onehot_array('../data/prueba/onlyseq.TSSnegFineGrained.hg17-test.neg')[0].astype(np.float32)
    
    y_train_pos = [1] * len(X_train_pos )
    y_train_neg = [0] * len(X_train_neg )
    y_val_pos = [1] * len(X_val_pos )
    y_val_neg = [0] * len(X_val_neg )
    y_test_pos = [1] * len(X_test_pos )
    y_test_neg = [0] * len(X_test_neg )

    X_train = np.concatenate((X_train_pos, X_train_neg))
    X_val = np.concatenate((X_val_pos, X_val_neg))
    X_test = np.concatenate((X_test_pos, X_test_neg))

    y_train = np.concatenate((y_train_pos, y_train_neg))
    y_val = np.concatenate((y_val_pos, y_val_neg))
    y_test = np.concatenate((y_test_pos, y_test_neg))


    if len(sys.argv) < 2:
        run_id = str(datetime.now()).replace(" ", "_").replace("-", "_").replace(":", "_").split(".")[0]
    else:
        run_id = sys.argv[1]
        #run_id = "".join(categories)

    log_file = "logs/"+run_id+".log"
    hist_file = "logs/"+run_id+".pkl"
    plot_file = "logs/"+run_id+".png"

    model = lstm_net()

    with open(log_file, 'w') as f:
        with redirect_stdout(f):
            #model.summary()

            #for layer in model.layers:
            #    print(layer.get_config())
            early_stopping_monitor = EarlyStopping( monitor='val_loss', min_delta=0, patience=15, 
                                                    verbose=1, mode='auto', baseline=None,
                                                    restore_best_weights=True)
            #reduce_lr_loss = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10, verbose=1, min_delta=1e-4, mode='min')

            history = model.fit(X_train, y_train,
                                shuffle=True,
                                batch_size=32,
                                epochs=100,
                                verbose=True,
                                validation_data=(X_val, y_val),
                                callbacks=[early_stopping_monitor])#, reduce_lr_loss])
            print("Train results:")
            test_results(X_train, y_train, model)
            print("Test results:")
            test_results(X_test, y_test, model)

    with open(hist_file, 'wb') as file_pi:
        pickle.dump(history.history, file_pi)

    plot_train_history(history.history, plot_file)