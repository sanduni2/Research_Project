"""
BROILER WEIGHT PREDICTION MODEL - EXTENDED RANGE (0-12 WEEKS)
Based on realistic broiler chicken growth curves
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import joblib
import json

print("="*80)
print("🐔 BROILER WEIGHT PREDICTION MODEL - EXTENDED RANGE (0-12 WEEKS)")
print("="*80)

# STEP 1: LOAD DATA
print("\n📂 Step 1: Loading Extended Broiler Growth Data...")
df = pd.read_csv('data/broiler_growth_extended.csv')
print(f"✅ Loaded {df.shape[0]} rows, {df.shape[1]} columns")
print(f"\n📊 Data Summary:")
print(f"   Age Range: {df['Age_Days'].min()} - {df['Age_Days'].max()} days")
print(f"   Weight Range: {df['Weight_g'].min()} - {df['Weight_g'].max()} grams")
print(f"   Diet Types: {df['Diet_Type'].unique().tolist()}")

# STEP 2: FEATURE ENGINEERING
print("\n🔧 Step 2: Feature Engineering...")

# Encode Diet Type
le = LabelEncoder()
df['Diet_Encoded'] = le.fit_transform(df['Diet_Type'])

# Create polynomial features for growth curve
df['Age_Squared'] = df['Age_Days'] ** 2
df['Age_Cubed'] = df['Age_Days'] ** 3

# Create interaction terms
df['Age_Diet_Interaction'] = df['Age_Days'] * df['Diet_Encoded']

print(f"✅ Features created: Age_Days, Age_Squared, Age_Cubed, Diet_Encoded, Age_Diet_Interaction")

# STEP 3: PREPARE FEATURES AND TARGET
print("\n📊 Step 3: Preparing Features and Target...")

# Define features
feature_cols = ['Age_Days', 'Age_Squared', 'Age_Cubed', 'Diet_Encoded', 'Age_Diet_Interaction']
X = df[feature_cols]
y = df['Weight_g']

print(f"   Features (X): {X.shape}")
print(f"   Target (y): {y.shape}")
print(f"\n   Weight Statistics:")
print(f"      Min: {y.min()}g")
print(f"      Max: {y.max()}g")
print(f"      Mean: {y.mean():.2f}g")
print(f"      Std: {y.std():.2f}g")

# STEP 4: SPLIT DATA
print("\n✂️ Step 4: Splitting Data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# STEP 5: FEATURE SCALING
print("\n⚖️ Step 5: Feature Scaling...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✅ Features scaled using StandardScaler")

# STEP 6: TRAIN MODELS
print("\n" + "="*80)
print("🤖 Step 6: Training Models...")
print("="*80)

models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    )
}

results = {}
best_model = None
best_score = -float('inf')
best_model_name = ""

for model_name, model in models.items():
    print(f"\n{'='*80}")
    print(f"📊 Training: {model_name}")
    print(f"{'='*80}")
    
    # Train
    if model_name == 'Linear Regression':
        model.fit(X_train_scaled, y_train)
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mae_test = mean_absolute_error(y_test, y_pred_test)
    mape_test = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
    
    results[model_name] = {
        'R2_Train': r2_train,
        'R2_Test': r2_test,
        'RMSE': rmse_test,
        'MAE': mae_test,
        'MAPE': mape_test
    }
    
    print(f"\n   📈 Performance Metrics:")
    print(f"      R² Score (Train): {r2_train:.4f}")
    print(f"      R² Score (Test):  {r2_test:.4f}")
    print(f"      RMSE:             {rmse_test:.2f}g")
    print(f"      MAE:              {mae_test:.2f}g")
    print(f"      MAPE:             {mape_test:.2f}%")
    
    # Track best model
    if r2_test > best_score:
        best_score = r2_test
        best_model = model
        best_model_name = model_name
        if model_name == 'Linear Regression':
            best_scaler = scaler

# STEP 7: SAVE BEST MODEL
print("\n" + "="*80)
print(f"💾 Step 7: Saving Best Model ({best_model_name})")
print("="*80)

# Save model
if best_model_name == 'Linear Regression':
    model_path = 'models/broiler_weight_prediction.pkl'
    scaler_path = 'models/broiler_weight_scaler.pkl'
    joblib.dump(best_model, model_path)
    joblib.dump(best_scaler, scaler_path)
    print(f"   ✅ Model saved: {model_path}")
    print(f"   ✅ Scaler saved: {scaler_path}")
else:
    model_path = 'models/broiler_weight_prediction.pkl'
    joblib.dump(best_model, model_path)
    print(f"   ✅ Model saved: {model_path}")

# Save metadata
metadata = {
    "model_name": best_model_name,
    "r2_score_train": results[best_model_name]['R2_Train'],
    "r2_score_test": results[best_model_name]['R2_Test'],
    "rmse": results[best_model_name]['RMSE'],
    "mae": results[best_model_name]['MAE'],
    "mape": results[best_model_name]['MAPE'],
    "features": feature_cols,
    "target": "Weight_g",
    "unit": "grams",
    "input_unit": "days",
    "age_range": f"{df['Age_Days'].min()}-{df['Age_Days'].max()} days",
    "diet_types": df['Diet_Type'].unique().tolist(),
    "training_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
}

metadata_path = 'models/broiler_weight_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=4)
print(f"   ✅ Metadata saved: {metadata_path}")

# STEP 8: TEST PREDICTIONS
print("\n" + "="*80)
print("🧪 Step 8: Testing Predictions for Different Ages")
print("="*80)

# Test at key ages (weeks 1-10)
test_ages = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70]  # 1-10 weeks
diet_encoded = 0  # Standard diet

print("\n   Predicted Weights (Standard Diet):")
print("   " + "-"*50)
for age in test_ages:
    weeks = age / 7
    age_sq = age ** 2
    age_cb = age ** 3
    interaction = age * diet_encoded
    
    test_features = np.array([[age, age_sq, age_cb, diet_encoded, interaction]])
    
    if best_model_name == 'Linear Regression':
        test_features_scaled = best_scaler.transform(test_features)
        pred_weight = best_model.predict(test_features_scaled)[0]
    else:
        pred_weight = best_model.predict(test_features)[0]
    
    print(f"   Week {weeks:.0f} ({age} days): {pred_weight:.0f}g")

print("\n" + "="*80)
print("✅ MODEL TRAINING COMPLETE!")
print("="*80)
print(f"\n   Best Model: {best_model_name}")
print(f"   R² Score: {best_score:.4f}")
print(f"   Model Path: {model_path}")
print("\n   🎯 Model ready for production use!")
print("="*80)
