import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# scikit-learn 相關匯入
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, 
    precision_score, recall_score, f1_score
)
from sklearn import tree
from matplotlib.colors import ListedColormap

# 1. 讀取 CSV 檔案
data = pd.read_csv('Churn_Modelling.csv')

# 2. 移除不必要的欄位: RowNumber, CustomerId, Surname
data = data.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1)


# 3. 檢查缺失值
print("\n各欄位缺失值數量：")
print(data.isnull().sum())
if data.isnull().values.any():
    print("\n資料中仍有缺失值。")
else:
    print("\n資料中沒有缺失值。")


# 4. 缺失值填補
# Geography：以眾數補值
# Age：以中位數補值
# HasCrCard, IsActiveMember：以眾數補值
data['Geography'] = data['Geography'].fillna(data['Geography'].mode()[0])
data['Age'] = data['Age'].fillna(data['Age'].median())
data['HasCrCard'] = data['HasCrCard'].fillna(data['HasCrCard'].mode()[0])
data['IsActiveMember'] = data['IsActiveMember'].fillna(data['IsActiveMember'].mode()[0])

print("\n缺失值填補後：")
print(data.isnull().sum())


# 5. 類別特徵轉換
# Label Encoding for Gender
# One-Hot Encoding for Geography
le = LabelEncoder()
data['Gender'] = le.fit_transform(data['Gender'])

ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
geo_encoded = ohe.fit_transform(data[['Geography']])
geo_encoded_df = pd.DataFrame(geo_encoded, columns=ohe.get_feature_names_out(['Geography']))
data = pd.concat([data.drop('Geography', axis=1), geo_encoded_df], axis=1)

print("\n轉換後資料前五行：")
print(data.head())


# 6. 定義特徵與標籤
# 特徵變數包含：CreditScore, Gender, Age, Tenure, Balance,
# NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, 
# Geography_France, Geography_Germany, Geography_Spain
features = ['CreditScore', 'Gender', 'Age', 'Tenure', 'Balance', 
            'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 
            'Geography_France', 'Geography_Germany', 'Geography_Spain']
X = data[features]
y = data['Exited']


# 7. 決策樹模型初始化（僅顯示模型參數）  
# 使用預設參數先進行初始化
dt_classifier = DecisionTreeClassifier()
print("\nDecision Tree 的初始參數：")
print(dt_classifier.get_params())


# 8. 分割資料 (訓練：測試 = 9:1) 並顯示各部分資料筆數
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
print("\n訓練資料筆數:", X_train.shape[0])
print("測試資料筆數:", X_test.shape[0])

# 9. 決策樹模型建立、訓練與預測
# 設定樹的最大深度為5
dt_classifier = DecisionTreeClassifier(max_depth=5, random_state=42)
dt_classifier.fit(X_train, y_train)
y_pred = dt_classifier.predict(X_test)

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

# 11. 繪製決策樹圖形
plt.figure(figsize=(20,10))
tree.plot_tree(dt_classifier, feature_names=X.columns, class_names=['0','1'], filled=True)
plt.title("Decision Tree Visualization (max_depth=5)")
plt.show()
