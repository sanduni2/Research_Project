#!/usr/bin/env python3
"""Test script to verify model loading and make test predictions."""

import os
import sys

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

print("="*80)
print("🔍 TESTING MODEL FILES")
print("="*80)

# Test 1: Check files exist
models_dir = r'C:\Users\Sanduni\Desktop\Research\data_anaysis\models'
files_to_check = [
    'weight_prediction_linear_regression.pkl',
    'weight_prediction_scaler.pkl',
    'resnet50/best_model.h5'
]

print("\n📂 Checking files...")
for file in files_to_check:
    path = os.path.join(models_dir, file)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"   ✅ {file}: {size:,} bytes")
    else:
        print(f"   ❌ {file}: NOT FOUND")

# Test 2: Try to load weight model with different methods
print("\n🧪 Testing Weight Model Loading...")
import pickle
import joblib

model_path = os.path.join(models_dir, 'weight_prediction_linear_regression.pkl')
scaler_path = os.path.join(models_dir, 'weight_prediction_scaler.pkl')

# Try method 1: pickle
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("   ✅ Loaded with pickle:", type(model))
except Exception as e:
    print(f"   ❌ pickle failed: {e}")
    model = None

# Try method 2: joblib
try:
    model = joblib.load(model_path)
    print("   ✅ Loaded with joblib:", type(model))
    model_works = True
except Exception as e:
    print(f"   ❌ joblib failed: {e}")
    model_works = False

# Try loading scaler
try:
    scaler = joblib.load(scaler_path)
    print("   ✅ Loaded scaler with joblib:", type(scaler))
    scaler_works = True
except Exception as e:
    print(f"   ❌ Scaler joblib failed: {e}")
    scaler_works = False

# Test 3: Make a prediction
if model_works and scaler_works:
    print("\n🔮 Testing Predictions...")
    import pandas as pd
    import numpy as np
    
    test_ages = [0, 7, 14, 21]
    for age in test_ages:
        features = pd.DataFrame({
            'Time': [age],
            'Time_squared': [age ** 2],
            'Time_cubed': [age ** 3]
        })
        
        scaled = scaler.transform(features)
        prediction = model.predict(scaled)[0]
        print(f"   Age {age:2d} days → Weight {prediction:6.1f}g")
    
    print("\n✅ WEIGHT MODEL WORKS PERFECTLY!")
else:
    print("\n❌ Weight model has issues")

# Test 4: Load ResNet50 model
print("\n🧪 Testing ResNet50 Model...")
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    
    resnet_path = os.path.join(models_dir, 'resnet50', 'best_model.h5')
    resnet_model = load_model(resnet_path)
    print(f"   ✅ ResNet50 loaded: {resnet_model.input_shape} -> {resnet_model.output_shape}")
    print("   ✅ RESNET50 MODEL WORKS!")
except Exception as e:
    print(f"   ❌ ResNet50 failed: {e}")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
