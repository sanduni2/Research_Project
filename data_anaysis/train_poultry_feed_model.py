"""
POULTRY FARM FEED CONSUMPTION MODEL TRAINING
Predict feed consumption based on weight growth and other farm factors

Dataset: poultry_farm_dataset.csv
Target: Feed_Consumption
Features: Weight_Growth, Temperature, Humidity, and others
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import joblib
import json

print("="*80)
print("🐓 POULTRY FARM MODEL TRAINING - Predict Feed Consumption")
print("="*80)

# =====================================
# STEP 1: LOAD DATA
# =====================================
print("\n📂 Step 1: Loading Data...")
df = pd.read_csv('data/poultry_farm_dataset.csv')
print(f"✅ Loaded {df.shape[0]} rows, {df.shape[1]} columns")
print(f"   Columns: {df.columns.tolist()}")

# =====================================
# STEP 2: DATA PREPROCESSING
# =====================================
print("\n🔧 Step 2: Data Preprocessing...")

# Check missing values
missing_values = df.isnull().sum()
print(f"\n   ❓ Missing Values:")
for col in missing_values[missing_values > 0].index:
    print(f"      - {col}: {missing_values[col]} ({missing_values[col]/len(df)*100:.2f}%)")

# Handle missing values in Disease_Incidence
if df['Disease_Incidence'].isnull().sum() > 0:
    print(f"\n   🔧 Handling missing values in Disease_Incidence...")
    df['Disease_Incidence'] = df['Disease_Incidence'].fillna('None')
    print(f"      ✅ Filled with 'None'")

# Check data types
print(f"\n   📊 Data Types:")
print(df.dtypes)

# =====================================
# STEP 3: FEATURE ENGINEERING
# =====================================
print("\n🔨 Step 3: Feature Engineering...")

# Encode categorical variables
print("   🏷️ Encoding categorical variables...")

# Disease_Incidence
le_disease = LabelEncoder()
df['Disease_Encoded'] = le_disease.fit_transform(df['Disease_Incidence'])
print(f"      ✅ Disease_Incidence encoded: {dict(enumerate(le_disease.classes_))}")

# Weather_Condition
le_weather = LabelEncoder()
df['Weather_Encoded'] = le_weather.fit_transform(df['Weather_Condition'])
print(f"      ✅ Weather_Condition encoded: {dict(enumerate(le_weather.classes_))}")

# Create interaction features
print("   🔧 Creating interaction features...")
df['Weight_Temp_interaction'] = df['Weight_Growth'] * df['Temperature']
df['Weight_Humidity_interaction'] = df['Weight_Growth'] * df['Humidity']
df['Mortality_Weight_ratio'] = df['Mortality_Rate'] / (df['Weight_Growth'] + 0.01)  # Avoid division by zero

print(f"   ✅ Created interaction features")

# =====================================
# STEP 4: FEATURE SELECTION
# =====================================
print("\n📊 Step 4: Selecting Features...")

# Calculate correlation with target (only numeric columns)
numeric_df = df.select_dtypes(include=[np.number])
correlations = numeric_df.corr()['Feed_Consumption'].sort_values(ascending=False)
print(f"\n   🔗 Feature Correlations with Feed_Consumption:")
print(correlations)

# Select features for modeling
# Important Note: Weight_Growth has very low correlation (-0.0008)
# We'll use multiple features to improve prediction
feature_cols = [
    'Weight_Growth',
    'Temperature',
    'Humidity',
    'Mortality_Rate',
    'Egg_Production',
    'Disease_Encoded',
    'Weather_Encoded',
    'Vaccination_Cost',
    'Labor_Hours',
    'Weight_Temp_interaction',
    'Weight_Humidity_interaction',
    'Mortality_Weight_ratio'
]

X = df[feature_cols]
y = df['Feed_Consumption']

print(f"\n   ✅ Selected Features: {feature_cols}")
print(f"   📊 Feature Matrix Shape: {X.shape}")
print(f"   📊 Target Vector Shape: {y.shape}")

print(f"\n   📈 Target Statistics (Feed_Consumption):")
print(f"      - Min: {y.min()}")
print(f"      - Max: {y.max()}")
print(f"      - Mean: {y.mean():.2f}")
print(f"      - Std: {y.std():.2f}")

# =====================================
# STEP 5: SPLIT DATA
# =====================================
print("\n✂️ Step 5: Splitting Data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   ✅ Training set: {X_train.shape[0]} samples")
print(f"   ✅ Test set: {X_test.shape[0]} samples")

# =====================================
# STEP 6: FEATURE SCALING
# =====================================
print("\n⚖️ Step 6: Feature Scaling...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✅ Features scaled using StandardScaler")

# Save preprocessing objects
joblib.dump(scaler, 'models/poultry_feed_scaler.pkl')
joblib.dump(le_disease, 'models/disease_encoder.pkl')
joblib.dump(le_weather, 'models/weather_encoder.pkl')
print("   💾 Preprocessing objects saved")

# =====================================
# STEP 7: TRAIN MODELS
# =====================================
print("\n" + "="*80)
print("🤖 Step 7: Training Multiple Models...")
print("="*80)

models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor(
        random_state=42, 
        max_depth=15,
        min_samples_split=20,
        min_samples_leaf=10
    ),
    'Random Forest': RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
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
    print(f"      ✓ R² Score:  {r2:.4f} {'⭐'*max(1, int(r2*5))}")
    print(f"      ✓ RMSE:      {rmse:.2f} kg")
    print(f"      ✓ MAE:       {mae:.2f} kg")
    print(f"      ✓ MAPE:      {mape:.2f}%")
    
    # Interpretation
    if r2 >= 0.85:
        print(f"      🎉 EXCELLENT! This model explains {r2*100:.1f}% of variance")
    elif r2 >= 0.70:
        print(f"      ✅ GOOD! This model explains {r2*100:.1f}% of variance")
    elif r2 >= 0.50:
        print(f"      ⚠️ MODERATE! This model explains {r2*100:.1f}% of variance")
    else:
        print(f"      ❌ POOR! This model only explains {r2*100:.1f}% of variance")
    
    # Feature importance (for tree-based models)
    if hasattr(model, 'feature_importances_'):
        print(f"\n   📊 Top 5 Important Features:")
        importances = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in importances.head(5).iterrows():
            print(f"      {row['feature']:<30} {row['importance']:.4f}")

# =====================================
# STEP 8: SELECT BEST MODEL
# =====================================
print("\n" + "="*80)
print("🏆 Step 8: Selecting Best Model")
print("="*80)

# Find best model based on R² score
best_model_name = max(results, key=lambda x: results[x]['R2_Score'])
best_model = results[best_model_name]['model']
best_r2 = results[best_model_name]['R2_Score']

print(f"\n   🥇 BEST MODEL: {best_model_name}")
print(f"   📊 R² Score: {best_r2:.4f}")
print(f"   📊 RMSE: {results[best_model_name]['RMSE']:.2f} kg")
print(f"   📊 MAE: {results[best_model_name]['MAE']:.2f} kg")
print(f"   📊 MAPE: {results[best_model_name]['MAPE']:.2f}%")

# =====================================
# STEP 9: SAVE MODELS
# =====================================
print("\n💾 Step 9: Saving Models...")

# Save best model
best_model_filename = f'models/poultry_feed_{best_model_name.lower().replace(" ", "_")}_model.pkl'
joblib.dump(best_model, best_model_filename)
print(f"   ✅ Best model saved: {best_model_filename}")

# Save all models for comparison
for model_name, result in results.items():
    filename = f'models/poultry_feed_{model_name.lower().replace(" ", "_")}_model.pkl'
    joblib.dump(result['model'], filename)
    print(f"   💾 Saved: {filename}")

# Save metrics and metadata
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
metrics['disease_classes'] = le_disease.classes_.tolist()
metrics['weather_classes'] = le_weather.classes_.tolist()

with open('results/metrics/poultry_feed_model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)
print(f"   ✅ Metrics saved: results/metrics/poultry_feed_model_metrics.json")

# =====================================
# STEP 10: TEST PREDICTIONS
# =====================================
print("\n" + "="*80)
print("🔮 Step 10: Testing Predictions")
print("="*80)

# Test with sample data
test_cases = [
    {
        'Weight_Growth': 1.2,
        'Temperature': 25,
        'Humidity': 0.55,
        'Mortality_Rate': 0.01,
        'Egg_Production': 1000,
        'Disease_Incidence': 'None',
        'Weather_Condition': 'Sunny',
        'Vaccination_Cost': 200,
        'Labor_Hours': 50,
        'description': 'Normal conditions, low weight gain'
    },
    {
        'Weight_Growth': 1.8,
        'Temperature': 28,
        'Humidity': 0.60,
        'Mortality_Rate': 0.015,
        'Egg_Production': 1100,
        'Disease_Incidence': 'Respiratory',
        'Weather_Condition': 'Cloudy',
        'Vaccination_Cost': 250,
        'Labor_Hours': 55,
        'description': 'Good growth, moderate conditions'
    },
    {
        'Weight_Growth': 1.5,
        'Temperature': 22,
        'Humidity': 0.50,
        'Mortality_Rate': 0.02,
        'Egg_Production': 950,
        'Disease_Incidence': 'Digestive',
        'Weather_Condition': 'Rainy',
        'Vaccination_Cost': 180,
        'Labor_Hours': 45,
        'description': 'Average growth, health issues'
    }
]

print("\n   🧪 Sample Predictions:")
for test_case in test_cases:
    # Prepare features
    test_data = {
        'Weight_Growth': test_case['Weight_Growth'],
        'Temperature': test_case['Temperature'],
        'Humidity': test_case['Humidity'],
        'Mortality_Rate': test_case['Mortality_Rate'],
        'Egg_Production': test_case['Egg_Production'],
        'Disease_Encoded': le_disease.transform([test_case['Disease_Incidence']])[0],
        'Weather_Encoded': le_weather.transform([test_case['Weather_Condition']])[0],
        'Vaccination_Cost': test_case['Vaccination_Cost'],
        'Labor_Hours': test_case['Labor_Hours'],
        'Weight_Temp_interaction': test_case['Weight_Growth'] * test_case['Temperature'],
        'Weight_Humidity_interaction': test_case['Weight_Growth'] * test_case['Humidity'],
        'Mortality_Weight_ratio': test_case['Mortality_Rate'] / (test_case['Weight_Growth'] + 0.01)
    }
    
    X_sample = pd.DataFrame([test_data])[feature_cols]
    
    # Predict
    if best_model_name == 'Linear Regression':
        X_sample_scaled = scaler.transform(X_sample)
        prediction = best_model.predict(X_sample_scaled)[0]
    else:
        prediction = best_model.predict(X_sample)[0]
    
    print(f"\n   📍 {test_case['description']}")
    print(f"      Input: Weight={test_case['Weight_Growth']} kg, Temp={test_case['Temperature']}°C, Humidity={test_case['Humidity']*100:.0f}%")
    print(f"      Predicted Feed Consumption: {prediction:.1f} kg")

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
print(f"   Scaler File: models/poultry_feed_scaler.pkl")

print("\n📱 For Web Application Integration:")
print("   Input Required:")
print("      - Weight_Growth (kg)")
print("      - Temperature (°C)")
print("      - Humidity (0-1)")
print("      - Mortality_Rate (0-1)")
print("      - Egg_Production (count)")
print("      - Disease_Incidence (None/Digestive/Respiratory/Other)")
print("      - Weather_Condition (Sunny/Cloudy/Clear/Rainy)")
print("      - Vaccination_Cost ($)")
print("      - Labor_Hours (hours)")
print(f"   Output: Predicted Feed Consumption (kg)")
print(f"   Expected Accuracy: {best_r2*100:.1f}% (R² = {best_r2:.4f})")

print("\n⚠️ NOTE:")
print("   Weight_Growth alone has very weak correlation with Feed_Consumption (-0.0008)")
print("   The model uses multiple features for better prediction accuracy")
print("   Consider collecting more diverse data for improved performance")

print("\n" + "="*80)
