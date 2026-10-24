import pandas as pd

print("="*80)
print("COLUMN ANALYSIS - Which Columns to Keep or Remove?")
print("="*80)

# ==========================================
# DATASET 1: chickweight.csv
# ==========================================
print("\n" + "="*80)
print("📊 DATASET 1: chickweight.csv")
print("="*80)

df1 = pd.read_csv('../data/chickweight.csv')

print(f"\n✅ Total Columns: {len(df1.columns)}")
print(f"✅ Total Rows: {len(df1)}")
print(f"\n📋 Column Details:\n")

for i, col in enumerate(df1.columns, 1):
    print(f"  {i}. {col:<20} ", end="")
    print(f"Type: {str(df1[col].dtype):<10} ", end="")
    print(f"Missing: {df1[col].isnull().sum():<6} ", end="")
    print(f"Unique: {df1[col].nunique():<6} ", end="")
    print(f"Example: {df1[col].iloc[0]}")

print(f"\n📊 First 5 Rows:")
print(df1.head())

print(f"\n💡 Purpose: Predict chicken weight from age/time")
print(f"🎯 Target Column: weight")
print(f"🔑 Important Columns: Time (age), Diet")
print(f"❓ Chick column: Individual chicken ID (may not be needed for prediction)")

# ==========================================
# DATASET 2: poultry_farm_dataset.csv
# ==========================================
print("\n\n" + "="*80)
print("📊 DATASET 2: poultry_farm_dataset.csv")
print("="*80)

df2 = pd.read_csv('../data/poultry_farm_dataset.csv')

print(f"\n✅ Total Columns: {len(df2.columns)}")
print(f"✅ Total Rows: {len(df2)}")
print(f"\n📋 Column Details:\n")

for i, col in enumerate(df2.columns, 1):
    print(f"  {i}. {col:<30} ", end="")
    print(f"Type: {str(df2[col].dtype):<10} ", end="")
    print(f"Missing: {df2[col].isnull().sum():<6} ", end="")
    print(f"Unique: {df2[col].nunique():<6} ", end="")
    if df2[col].dtype == 'object':
        print(f"Values: {df2[col].unique()[:3].tolist()}")
    else:
        print(f"Range: {df2[col].min():.1f} - {df2[col].max():.1f}")

print(f"\n📊 First 3 Rows:")
print(df2.head(3).to_string())

print(f"\n💡 Purpose: Predict feed consumption")
print(f"🎯 Target Column: Feed_Consumption")
print(f"🔑 Important Columns: Weight_Growth, Temperature, Humidity")
print(f"❓ Less Important: Revenue, Expenses (these are outcomes, not predictors)")

# ==========================================
# RECOMMENDATIONS
# ==========================================
print("\n\n" + "="*80)
print("💡 RECOMMENDATIONS FOR COLUMN REMOVAL")
print("="*80)

print("\n📌 DATASET 1: chickweight.csv")
print("-" * 80)
print("Keep These (Needed for Prediction):")
print("  ✅ weight       - TARGET (what we predict)")
print("  ✅ Time         - Age of chicken (main predictor)")
print("  ✅ Diet         - Feed type (important for optimization)")
print("\nMaybe Remove:")
print("  ❓ Chick        - Individual chicken ID")
print("                   (Not needed if we predict for average flock)")
print("                   (Keep it if you want individual tracking)")

print("\n📌 DATASET 2: poultry_farm_dataset.csv")
print("-" * 80)
print("Keep These (Needed for Prediction):")
print("  ✅ Feed_Consumption     - TARGET (what we predict)")
print("  ✅ Weight_Growth        - Main predictor")
print("  ✅ Temperature          - Environmental factor")
print("  ✅ Humidity             - Environmental factor")
print("  ✅ Mortality_Rate       - Health indicator")
print("  ✅ Disease_Incidence    - Health indicator")
print("  ✅ Weather_Condition    - Environmental factor")

print("\nProbably Remove (Less Important):")
print("  ❌ Egg_Production       - Not related to broiler chickens")
print("  ❌ Revenue              - This is an OUTCOME, not a predictor")
print("  ❌ Expenses             - This is an OUTCOME, not a predictor")
print("  ❌ Inventory_Feed       - Not directly related to consumption")
print("  ❌ Inventory_Medication - Not directly related to consumption")

print("\nMaybe Keep:")
print("  ❓ Vaccination_Cost     - Could indicate health spending")
print("  ❓ Labor_Hours          - Could indicate farm activity level")

print("\n" + "="*80)
print("❓ PLEASE TELL ME WHICH COLUMNS TO REMOVE:")
print("="*80)
print("\nI'll wait for your decision before creating the preprocessing scripts!")
print("\nExample answer:")
print('  "Remove Chick from dataset 1"')
print('  "Remove Revenue, Expenses, Egg_Production from dataset 2"')
print("="*80)
