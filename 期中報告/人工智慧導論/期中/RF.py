import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, recall_score,
    f1_score, classification_report
)
from sklearn.tree import plot_tree

# 1. 讀取資料
df = pd.read_csv('Churn_Modelling.csv')

# 2. 移除無用欄位
df.drop(['RowNumber', 'CustomerId', 'Surname'], axis=1, inplace=True)

# 3. 缺失值處理
df['Geography'] = df['Geography'].fillna(df['Geography'].mode()[0])
df['Age'] = df['Age'].fillna(df['Age'].median())
df['HasCrCard'] = df['HasCrCard'].fillna(df['HasCrCard'].mode()[0])
df['IsActiveMember'] = df['IsActiveMember'].fillna(df['IsActiveMember'].mode()[0])

# 4. 類別欄位編碼
le = LabelEncoder()
df['Gender'] = le.fit_transform(df['Gender'])  # Male=1, Female=0

ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
geo_encoded = ohe.fit_transform(df[['Geography']])
geo_encoded_df = pd.DataFrame(geo_encoded, columns=ohe.get_feature_names_out(['Geography']))
df = pd.concat([df.drop('Geography', axis=1), geo_encoded_df], axis=1)

# 5. 定義特徵與目標變數
X = df.drop('Exited', axis=1)
y = df['Exited']

# 6. 分割資料集（訓練：測試 = 9:1）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
print(f"\n訓練資料筆數: {X_train.shape[0]}")
print(f"測試資料筆數: {X_test.shape[0]}")

# 7. 隨機森林初始化與訓練
rf_classifier = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
print("\n隨機森林模型參數：")
rf_classifier.get_params()

rf_classifier.fit(X_train, y_train)

# 8. 模型預測
y_pred = rf_classifier.predict(X_test)

# 9. 評估模型
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

# 10. 繪製隨機森林中的一棵樹
plt.figure(figsize=(20, 10))
plot_tree(rf_classifier.estimators_[0], feature_names=X.columns, class_names=['Not Churned', 'Churned'], filled=True, rounded=True)
plt.show()
