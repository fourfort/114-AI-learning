#SVM
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# scikit-learn 相關匯入
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, classification_report,confusion_matrix, precision_score, recall_score, f1_score)
from matplotlib.colors import ListedColormap
from sklearn.decomposition import PCA

### 1. 讀取資料
df = pd.read_csv('Churn_Modelling.csv')

### 2. 資料預處理
# 移除不必要的欄位
df = df.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1)

# 檢查缺失值
missing_values = df.isnull().sum()
print("Missing values in each column:\n", missing_values)
if df.isnull().values.any():
    print("\nThere are missing values in the DataFrame.")
else:
    print("\nThere are no missing values in the DataFrame.")

# 補值：Geography 用眾數, Age 用中位數, HasCrCard 與 IsActiveMember 用眾數
df['Geography'] = df['Geography'].fillna(df['Geography'].mode()[0])
df['Age'] = df['Age'].fillna(df['Age'].median())
df['HasCrCard'] = df['HasCrCard'].fillna(df['HasCrCard'].mode()[0])
df['IsActiveMember'] = df['IsActiveMember'].fillna(df['IsActiveMember'].mode()[0])

# 再次檢查缺失值
print("\nMissing values after imputation:\n", df.isnull().sum())
if df.isnull().values.any():
    print("\nThere are still missing values.")
else:
    print("\nThere are no missing values.")

# 類別特徵轉換
# Label Encoding for Gender
le = LabelEncoder()
df['Gender'] = le.fit_transform(df['Gender'])

# One-Hot Encoding for Geography
ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
geography_encoded = ohe.fit_transform(df[['Geography']])
geography_encoded_df = pd.DataFrame(geography_encoded,columns=ohe.get_feature_names_out(['Geography']))
# 合併並移除原 Geography 欄位
df = pd.concat([df.drop('Geography', axis=1), geography_encoded_df], axis=1)

### 3. 定義特徵與標籤
features = ['CreditScore', 'Gender', 'Age', 'Tenure', 'Balance', 
            'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 
            'Geography_France', 'Geography_Germany', 'Geography_Spain']
X = df[features]
y = df['Exited']

### 4. 資料分割與標準化 (分割比例 7:3)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print("\nNumber of training samples:", len(X_train))
print("Number of testing samples:", len(X_test))

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

### 5. SVM 模型建立、訓練與預測 (未特定調參)
svm_model = SVC(kernel='rbf', probability=True, random_state=42)
svm_model.fit(X_train_scaled, y_train)
y_pred = svm_model.predict(X_test_scaled)

### 6. 評估模型
print("\n--- Model Evaluation ---")
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:\n", cm)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix")
plt.show()

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

### 7. 多特徵決策邊界視覺化：利用 PCA 將 12 維降至 2 維
# 對全部訓練資料進行 PCA 降維，n_components=2
pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_train_scaled)
X_test_pca = pca.transform(X_test_scaled)

# 用降維後資料訓練 SVM 模型（可重新設定超參數）
svm_pca = SVC(kernel='rbf', probability=True, random_state=42)
svm_pca.fit(X_train_pca, y_train)

# 產生網格座標以畫決策邊界
x_min, x_max = X_train_pca[:, 0].min() - 1, X_train_pca[:, 0].max() + 1
y_min, y_max = X_train_pca[:, 1].min() - 1, X_train_pca[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01),
                     np.arange(y_min, y_max, 0.01))

Z = svm_pca.predict(np.array([xx.ravel(), yy.ravel()]).T)
Z = Z.reshape(xx.shape)

plt.figure(figsize=(10, 6))
plt.contourf(xx, yy, Z, alpha=0.75, cmap=ListedColormap(('red', 'green')))
plt.scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=y_train, edgecolors='k', cmap=ListedColormap(('red', 'green')))
plt.title('SVM Decision Boundary in PCA-reduced Space')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.show()
