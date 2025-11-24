# file: model_trainer.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import joblib
import os
import database as db

def create_sequences(dataset, look_back=12):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

def fine_tune_model_for_user(user_id: int):
    """
    Fetches a user's entire glucose history and fine-tunes a new
    prediction model specifically for them.
    """
    print(f"--- [Trainer] Starting fine-tuning for user {user_id}... ---")
    
    # 1. Fetch all data for the user
    glucose_history = db.get_recent_glucose_readings(user_id, limit=9999) # Get all data
    
    if len(glucose_history) < 200: # Need a minimum amount of data to train
        print(f"--- [Trainer] User {user_id} has insufficient data ({len(glucose_history)} readings). Aborting. ---")
        return

    print(f"--- [Trainer] Fetched {len(glucose_history)} readings from database. ---")
    
    # 2. Preprocess the data (similar to Colab)
    dataset = np.array(glucose_history).reshape(-1, 1).astype('float32')
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    
    trainX, trainY = create_sequences(dataset)
    trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))

    # 3. Build and train a new model
    model = Sequential()
    model.add(LSTM(16, input_shape=(trainX.shape[1], trainX.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    print(f"--- [Trainer] Training new model on user data... ---")
    # In a real app, this might be more epochs, but 5 is fast for a demo.
    model.fit(trainX, trainY, epochs=5, batch_size=32, verbose=0)
    
    # 4. Save the personalized model and scaler
    user_model_path = f'glucose_predictor_user_{user_id}.h5'
    user_scaler_path = f'scaler_user_{user_id}.gz'
    
    model.save(user_model_path)
    joblib.dump(scaler, user_scaler_path)
    
    print(f"--- [Trainer] SUCCESS: Saved personalized model to {user_model_path} ---")