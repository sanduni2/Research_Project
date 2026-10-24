import pandas as pd
import numpy as np

print("="*60)
print("DATASET ANALYSIS FOR MODEL SELECTION")
print("="*60)

# ====================
# CHICKWEIGHT DATASET
# ====================
print("\n" + "="*60)
print("1. CHICKWEIGHT.CSV - Predict Weight from Age/Time")
print("="*60)

df_chickweight = pd.read_csv('data/chickweight.csv')

print(f"\n📊 Dataset Shape: {df_chickweight.shape[0]} rows, {df_chickweight.shape[1]} columns")
print(f"\n📋 Columns: {df_chickweight.columns.tolist()}")
print(f"\n🔢 Data Types:\n{df_chickweight.dtypes}")

print(f"\n📈 Basic Statistics:")
print(df_chickweight.describe())

print(f"\n❓ Missing Values:")
print(df_chickweight.isnull().sum())

print(f"\n🐔 Unique Values:")
print(f"  - Number of Chicks: {df_chickweight['Chick'].nunique()}")
print(f"  - Diet Types: {sorted(df_chickweight['Diet'].unique())}")
print(f"  - Time Points: {sorted(df_chickweight['Time'].unique())}")

print(f"\n📊 Weight Range: {df_chickweight['weight'].min()} - {df_chickweight['weight'].max()} grams")
print(f"📊 Time Range: {df_chickweight['Time'].min()} - {df_chickweight['Time'].max()} days")

# Check correlations
print(f"\n🔗 Correlation Matrix:")
print(df_chickweight.corr())

# ====================
# POULTRY FARM DATASET
# ====================
print("\n\n" + "="*60)
print("2. POULTRY_FARM_DATASET.CSV - Predict Feed Consumption from Weight")
print("="*60)

df_poultry = pd.read_csv('data/poultry_farm_dataset.csv')

print(f"\n📊 Dataset Shape: {df_poultry.shape[0]} rows, {df_poultry.shape[1]} columns")
print(f"\n📋 Columns: {df_poultry.columns.tolist()}")
print(f"\n🔢 Data Types:\n{df_poultry.dtypes}")

print(f"\n📈 Basic Statistics:")
print(df_poultry.describe())

print(f"\n❓ Missing Values:")
print(df_poultry.isnull().sum())

# Focus on Feed_Consumption and Weight_Growth
print(f"\n🎯 Target Variable (Feed_Consumption):")
print(f"  - Range: {df_poultry['Feed_Consumption'].min()} - {df_poultry['Feed_Consumption'].max()}")
print(f"  - Mean: {df_poultry['Feed_Consumption'].mean():.2f}")
print(f"  - Std Dev: {df_poultry['Feed_Consumption'].std():.2f}")

print(f"\n🎯 Feature Variable (Weight_Growth):")
print(f"  - Range: {df_poultry['Weight_Growth'].min():.2f} - {df_poultry['Weight_Growth'].max():.2f} kg")
print(f"  - Mean: {df_poultry['Weight_Growth'].mean():.2f} kg")
print(f"  - Std Dev: {df_poultry['Weight_Growth'].std():.2f} kg")

# Check correlation between Weight_Growth and Feed_Consumption
correlation = df_poultry['Weight_Growth'].corr(df_poultry['Feed_Consumption'])
print(f"\n🔗 Correlation (Weight_Growth vs Feed_Consumption): {correlation:.4f}")

# Check for categorical variables
categorical_cols = df_poultry.select_dtypes(include=['object']).columns.tolist()
print(f"\n📑 Categorical Columns: {categorical_cols}")
for col in categorical_cols:
    print(f"  - {col}: {df_poultry[col].nunique()} unique values - {df_poultry[col].unique()[:5]}")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)

# ====================
# MODEL RECOMMENDATIONS
# ====================
print("\n\n" + "="*60)
print("🎯 MODEL RECOMMENDATIONS")
print("="*60)

print("\n1️⃣ CHICKWEIGHT.CSV (Weight Prediction from Time/Age)")
print("-" * 60)
print("Task: Regression (Predict continuous weight value)")
print("\nRecommended Models (Best to Test):")
print("  ✅ 1. Random Forest Regressor (BEST CHOICE)")
print("     - Handles non-linear growth patterns")
print("     - Can capture diet differences")
print("     - Robust to outliers")
print("     - Expected Accuracy: R² = 0.90-0.95")
print("\n  ✅ 2. XGBoost Regressor (EXCELLENT)")
print("     - High accuracy for tabular data")
print("     - Handles feature interactions well")
print("     - Expected Accuracy: R² = 0.92-0.96")
print("\n  ✅ 3. Linear Regression (BASELINE)")
print("     - Simple and interpretable")
print("     - Good for linear growth phases")
print("     - Expected Accuracy: R² = 0.85-0.90")
print("\n  ⚠️  4. Decision Tree (NOT RECOMMENDED)")
print("     - Tends to overfit")
print("     - Use Random Forest instead")

print("\n2️⃣ POULTRY_FARM_DATASET.CSV (Feed Consumption Prediction)")
print("-" * 60)
print("Task: Regression (Predict continuous feed consumption)")
print(f"Note: Correlation between Weight & Feed = {correlation:.4f}")

if abs(correlation) > 0.7:
    print("✅ Strong correlation detected - Good for prediction!")
elif abs(correlation) > 0.4:
    print("⚠️ Moderate correlation - May need additional features")
else:
    print("❌ Weak correlation - Consider using more features")

print("\nRecommended Models (Best to Test):")
print("  ✅ 1. Random Forest Regressor (BEST CHOICE)")
print("     - Handles multiple features well")
print("     - Can use other variables (temperature, humidity, etc.)")
print("     - Expected Accuracy: R² = 0.80-0.90")
print("\n  ✅ 2. XGBoost Regressor (EXCELLENT)")
print("     - Great for complex relationships")
print("     - Expected Accuracy: R² = 0.85-0.92")
print("\n  ✅ 3. Multiple Linear Regression (BASELINE)")
print("     - Use Weight_Growth + Temperature + Humidity")
print("     - Expected Accuracy: R² = 0.70-0.80")

print("\n" + "="*60)
print("📊 RECOMMENDED APPROACH")
print("="*60)
print("\n1. Start with Linear Regression (baseline)")
print("2. Try Random Forest (likely best performance)")
print("3. Try XGBoost (for comparison)")
print("4. Compare all models using R², RMSE, MAE")
print("5. Select the model with best R² score")
print("\n✅ Random Forest is recommended as the BEST starting point!")
print("="*60)
