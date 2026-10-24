"""
CHICKWEIGHT MODEL TRAINING
Predict chicken weight based on age (Time) and Diet

Dataset: chickweight.csv
Target: weight (grams)
Features: Time (days), Diet (1-4)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import joblib
import json

print("="*80)
print("🐔 CHICKWEIGHT MODEL TRAINING - Predict Weight from Age/Time")
print("="*80)

# =====================================
# STEP 1: LOAD DATA
# =====================================
print("\n📂 Step 1: Loading Data...")
df = pd.read_csv('data/chickweight.csv')
print(f"✅ Loaded {df.shape[0]} rows, {df.shape[1]} columns")
print(f"   Columns: {df.columns.tolist()}")

# =====================================
# STEP 2: DATA PREPROCESSING
# =====================================
print("\n🔧 Step 2: Data Preprocessing...")

# Check for missing values
missing_values = df.isnull().sum()
print(f"\n   Missing Values:")
print(missing_values)

if missing_values.sum() > 0:
    print("   ⚠️ Handling missing values...")
    df = df.dropna()
    print(f"   ✅ Rows after removing missing values: {df.shape[0]}")
else:
    print("   ✅ No missing values found!")

# Feature Engineering
print("\n   🔨 Feature Engineering...")

# Create interaction features
df['Time_squared'] = df['Time'] ** 2  # Non-linear growth
df['Time_Diet_interaction'] = df['Time'] * df['Diet']  # Diet effect over time

# Create dummy variables for Diet (One-Hot Encoding)
diet_dummies = pd.get_dummies(df['Diet'], prefix='Diet', drop_first=False)
df = pd.concat([df, diet_dummies], axis=1)

print(f"   ✅ Created additional features")
print(f"   📊 Final dataset shape: {df.shape}")
print(f"   📋 Features: {df.columns.tolist()}")

# =====================================
# STEP 3: PREPARE FEATURES AND TARGET
# =====================================
print("\n📊 Step 3: Preparing Features and Target...")

# Define features (X) and target (y)
# We'll use Time, Diet, and engineered features
feature_cols = ['Time', 'Diet', 'Time_squared', 'Time_Diet_interaction', 
                'Diet_1', 'Diet_2', 'Diet_3', 'Diet_4']
X = df[feature_cols]
y = df['weight']

print(f"   ✅ Features (X): {X.shape}")
print(f"   ✅ Target (y): {y.shape}")
print(f"\n   📈 Target Statistics:")
print(f"      - Min weight: {y.min()} grams")
print(f"      - Max weight: {y.max()} grams")
print(f"      - Mean weight: {y.mean():.2f} grams")
print(f"      - Std weight: {y.std():.2f} grams")

# =====================================
# STEP 4: SPLIT DATA
# =====================================
print("\n✂️ Step 4: Splitting Data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   ✅ Training set: {X_train.shape[0]} samples")
print(f"   ✅ Test set: {X_test.shape[0]} samples")

# =====================================
# STEP 5: FEATURE SCALING
# =====================================
print("\n⚖️ Step 5: Feature Scaling...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✅ Features scaled using StandardScaler")

# Save the scaler
joblib.dump(scaler, 'models/chickweight_scaler.pkl')
print("   💾 Scaler saved: models/chickweight_scaler.pkl")

# =====================================
# STEP 6: TRAIN MODELS
# =====================================
print("\n" + "="*80)
print("🤖 Step 6: Training Multiple Models...")
print("="*80)

models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor(random_state=42, max_depth=10),
    'Random Forest': RandomForestRegressor(
        n_estimators=100, 
        max_depth=15, 
        random_state=42,
        n_jobs=-1
    )
}

results = {}

for model_name, model in models.items():
    print(f"\n{'='*80}")
    print(f"📊 Training: {model_name}")
    print(f"{'='*80}")
    
    # Train model
    if model_name == 'Linear Regression':
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    
    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    results[model_name] = {
        'R2_Score': r2,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape,
        'model': model
    }
    
    print(f"\n   📈 Performance Metrics:")
    print(f"      ✓ R² Score:  {r2:.4f} {'⭐'*int(r2*5)}")
    print(f"      ✓ RMSE:      {rmse:.2f} grams")
    print(f"      ✓ MAE:       {mae:.2f} grams")
    print(f"      ✓ MAPE:      {mape:.2f}%")
    
    # Interpretation
    if r2 >= 0.90:
        print(f"      🎉 EXCELLENT! This model explains {r2*100:.1f}% of variance")
    elif r2 >= 0.80:
        print(f"      ✅ GOOD! This model explains {r2*100:.1f}% of variance")
    elif r2 >= 0.70:
        print(f"      ⚠️ MODERATE! This model explains {r2*100:.1f}% of variance")
    else:
        print(f"      ❌ POOR! This model only explains {r2*100:.1f}% of variance")

# =====================================
# STEP 7: SELECT BEST MODEL
# =====================================
print("\n" + "="*80)
print("🏆 Step 7: Selecting Best Model")
print("="*80)

# Find best model based on R² score
best_model_name = max(results, key=lambda x: results[x]['R2_Score'])
best_model = results[best_model_name]['model']
best_r2 = results[best_model_name]['R2_Score']

print(f"\n   🥇 BEST MODEL: {best_model_name}")
print(f"   📊 R² Score: {best_r2:.4f}")
print(f"   📊 RMSE: {results[best_model_name]['RMSE']:.2f} grams")
print(f"   📊 MAE: {results[best_model_name]['MAE']:.2f} grams")
print(f"   📊 MAPE: {results[best_model_name]['MAPE']:.2f}%")

# =====================================
# STEP 8: SAVE BEST MODEL
# =====================================
print("\n💾 Step 8: Saving Models...")

# Save best model
best_model_filename = f'models/chickweight_{best_model_name.lower().replace(" ", "_")}_model.pkl'
joblib.dump(best_model, best_model_filename)
print(f"   ✅ Best model saved: {best_model_filename}")

# Save all models for comparison
for model_name, result in results.items():
    filename = f'models/chickweight_{model_name.lower().replace(" ", "_")}_model.pkl'
    joblib.dump(result['model'], filename)
    print(f"   💾 Saved: {filename}")

# Save metrics
metrics = {
    model_name: {
        'R2_Score': float(result['R2_Score']),
        'RMSE': float(result['RMSE']),
        'MAE': float(result['MAE']),
        'MAPE': float(result['MAPE'])
    }
    for model_name, result in results.items()
}

metrics['best_model'] = best_model_name
metrics['feature_columns'] = feature_cols

with open('results/metrics/chickweight_model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)
print(f"   ✅ Metrics saved: results/metrics/chickweight_model_metrics.json")

# =====================================
# STEP 9: TEST PREDICTIONS
# =====================================
print("\n" + "="*80)
print("🔮 Step 9: Testing Predictions")
print("="*80)

# Test with sample data
test_cases = [
    {'Time': 0, 'Diet': 1, 'description': 'Day 0, Diet 1 (newborn)'},
    {'Time': 10, 'Diet': 1, 'description': 'Day 10, Diet 1'},
    {'Time': 21, 'Diet': 1, 'description': 'Day 21, Diet 1 (harvest)'},
    {'Time': 10, 'Diet': 4, 'description': 'Day 10, Diet 4 (premium)'},
    {'Time': 21, 'Diet': 4, 'description': 'Day 21, Diet 4 (premium harvest)'}
]

print("\n   🧪 Sample Predictions:")
for test_case in test_cases:
    # Prepare features
    test_data = {
        'Time': test_case['Time'],
        'Diet': test_case['Diet'],
        'Time_squared': test_case['Time'] ** 2,
        'Time_Diet_interaction': test_case['Time'] * test_case['Diet'],
        'Diet_1': 1 if test_case['Diet'] == 1 else 0,
        'Diet_2': 1 if test_case['Diet'] == 2 else 0,
        'Diet_3': 1 if test_case['Diet'] == 3 else 0,
        'Diet_4': 1 if test_case['Diet'] == 4 else 0
    }
    
    X_sample = pd.DataFrame([test_data])[feature_cols]
    
    # Predict
    if best_model_name == 'Linear Regression':
        X_sample_scaled = scaler.transform(X_sample)
        prediction = best_model.predict(X_sample_scaled)[0]
    else:
        prediction = best_model.predict(X_sample)[0]
    
    print(f"\n   📍 {test_case['description']}")
    print(f"      Predicted Weight: {prediction:.1f} grams ({prediction/1000:.3f} kg)")

# =====================================
# SUMMARY
# =====================================
print("\n" + "="*80)
print("✅ TRAINING COMPLETE!")
print("="*80)

print(f"\n📊 Model Comparison:")
print(f"{'Model':<20} {'R² Score':<12} {'RMSE':<12} {'MAE':<12} {'Status':<15}")
print("-" * 80)
for model_name, result in sorted(results.items(), key=lambda x: x[1]['R2_Score'], reverse=True):
    status = "🥇 BEST" if model_name == best_model_name else ""
    print(f"{model_name:<20} {result['R2_Score']:<12.4f} {result['RMSE']:<12.2f} {result['MAE']:<12.2f} {status:<15}")

print(f"\n💡 Recommendation:")
print(f"   Use '{best_model_name}' for your web application")
print(f"   Model File: {best_model_filename}")
print(f"   Scaler File: models/chickweight_scaler.pkl")

print("\n📱 For Web Application Integration:")
print("   Input Required: Time (days), Diet (1-4)")
print("   Output: Predicted Weight (grams)")
print(f"   Expected Accuracy: {best_r2*100:.1f}% (R² = {best_r2:.4f})")

print("\n" + "="*80)
