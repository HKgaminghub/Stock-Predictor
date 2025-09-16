import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler

# Load dataset (first 1000 rows)
df = pd.read_csv("C:/Users/hardb/Downloads/archive (3)/housing.csv").head(1000)

# Select only 'median_house_value' column
column = 'median_house_value'
original = df[[column]]

# Apply RobustScaler
scaler = RobustScaler()
scaled = scaler.fit_transform(original)
scaled_df = pd.DataFrame(scaled, columns=[column])

# Create one figure with two separate KDE plots (before and after)
plt.figure(figsize=(12, 5))

# Subplot 1 - Before Scaling
plt.subplot(1, 2, 1)
sns.kdeplot(data=original[column], fill=True, color='blue')
plt.title("Before Robust Scaling")
plt.xlabel(column)
plt.grid(True)

# Subplot 2 - After Scaling
plt.subplot(1, 2, 2)
sns.kdeplot(data=scaled_df[column], fill=True, color='green')
plt.title("After Robust Scaling")
plt.xlabel(column + " (Scaled)")
plt.grid(True)

# Layout and show
plt.tight_layout()
plt.suptitle("Robust Scaling - median_house_value", fontsize=16, y=1.05)
plt.show()