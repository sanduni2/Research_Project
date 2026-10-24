"""
Test the broiler weight prediction model
"""
import joblib
import numpy as np

# Load model and scaler
model = joblib.load('models/broiler_weight_prediction.pkl')
scaler = joblib.load('models/broiler_weight_scaler.pkl')

print("✅ Model and scaler loaded")
print(f"   Model type: {type(model)}")
print(f"   Scaler type: {type(scaler)}")

# Test prediction for 70 days, Standard diet
age = 70
diet_encoded = 2  # Standard diet
age_squared = age ** 2
age_cubed = age ** 3
age_diet_interaction = age * diet_encoded

print(f"\n🧪 Test Input:")
print(f"   Age: {age} days")
print(f"   Age²: {age_squared}")
print(f"   Age³: {age_cubed}")
print(f"   Diet: {diet_encoded} (Standard)")
print(f"   Interaction: {age_diet_interaction}")

# Create features
features = np.array([[age, age_squared, age_cubed, diet_encoded, age_diet_interaction]])
print(f"\n   Features shape: {features.shape}")
print(f"   Features: {features}")

# Scale features
features_scaled = scaler.transform(features)
print(f"\n   Scaled features: {features_scaled}")

# Predict
predicted_weight = model.predict(features_scaled)[0]

print(f"\n✅ PREDICTION:")
print(f"   Predicted Weight: {predicted_weight:.2f}g")
print(f"   Expected: ~4757g (from training data)")
print(f"   Difference: {abs(predicted_weight - 4757):.2f}g")
