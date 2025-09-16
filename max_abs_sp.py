import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MaxAbsScaler
from scipy import sparse

# Step 1: Load the uploaded dataset
df = pd.read_csv("C:/Users/hardb/Downloads/archive (3)/max_abs_sparse_data.csv")

# Step 2: Apply MaxAbsScaler to numeric columns
scaler = MaxAbsScaler()
scaled_data = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_data, columns=df.columns)

# Step 3: Convert to sparse matrix
sparse_matrix = sparse.csr_matrix(scaled_data)
print("Sparse matrix shape:", sparse_matrix.shape)
print("Sparsity: {:.2f}%".format(100 * (1.0 - sparse_matrix.count_nonzero() / sparse_matrix.size)))

# Step 4: Plot before and after (side-by-side)
plt.figure(figsize=(18, 12))

for i, column in enumerate(df.columns):
    plt.subplot(4, 4, 2*i + 1)
    sns.kdeplot(df[column], fill=True, color='blue')
    plt.title(f"Before Scaling: {column}")
    plt.grid(True)

    plt.subplot(4, 4, 2*i + 2)
    sns.kdeplot(scaled_df[column], fill=True, color='green')
    plt.title(f"After MaxAbs Scaling: {column}")
    plt.grid(True)

plt.tight_layout()
plt.suptitle("Before vs After MaxAbs Normalization (Seaborn KDE)", fontsize=18, y=1.02)
plt.show()