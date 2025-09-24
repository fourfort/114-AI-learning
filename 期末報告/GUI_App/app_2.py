import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import shutil
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.tree import export_text

# 建立主視窗
root = tk.Tk()
root.title("人工智慧數據分析系統")
root.geometry("800x600")

# 左側按鈕區塊
left_frame = tk.Frame(root, width=200)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

uploaded_filename = None  # 用來儲存上傳的檔案名稱

# 上傳 Excel 檔案並儲存到當前資料夾
def upload_file():
    global uploaded_filename
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if file_path:
        try:
            filename = os.path.basename(file_path)
            target_path = os.path.join(os.getcwd(), filename)

            if os.path.abspath(file_path) != os.path.abspath(target_path):
                shutil.copy(file_path, target_path)
                text_area.insert(tk.END, f"✅ 檔案已複製並儲存為：{filename}\n")
            else:
                text_area.insert(tk.END, f"✅ 檔案已存在於目標資料夾：{filename}\n")

            uploaded_filename = filename  # 記錄檔案名稱
        except Exception as e:
            text_area.insert(tk.END, f"❌ 檔案讀取失敗：{e}\n")

# 執行決策樹分析
def run_analysis():
    if not uploaded_filename:
        messagebox.showwarning("提醒", "請先上傳檔案")
        return

    try:
        # 讀取檔案
        df = pd.read_excel(uploaded_filename)
        if df.shape[1] < 2:
            text_area.insert(tk.END, "❌ 檔案欄位數不足，請確認檔案內容。\n")
            return

        text_area.insert(tk.END, "📈 開始執行決策樹分析...\n")
        text_area.insert(tk.END, f"資料筆數：{len(df)}，欄位數：{len(df.columns)}\n")

        # 分割特徵與目標欄位
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]

        # 建議使用 70% 資料做訓練
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # 建議最大深度為 3
        clf = DecisionTreeClassifier(max_depth=3, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        # 顯示決策樹分類流程（文字版）
        tree_rules = export_text(clf, feature_names=list(X.columns))
        text_area.insert(tk.END, "\n📋 決策樹分類規則：\n")
        text_area.insert(tk.END, f"{tree_rules}\n")

        text_area.insert(tk.END, f"✅ 分析完成！\n")
        text_area.insert(tk.END, f"準確率：{acc:.2f}\n")
        text_area.insert(tk.END, f"預測結果（前10筆）：\n{y_pred[:10]}\n\n")

    except Exception as e:
        text_area.insert(tk.END, f"❌ 決策樹分析錯誤：{e}\n")



btn_upload = tk.Button(left_frame, text="分析檔案上傳（Excel）", command=upload_file, width=20, height=2)
btn_upload.pack(pady=20)

btn_analyze = tk.Button(left_frame, text="數據分析（決策樹）", command=run_analysis, width=20, height=2)
btn_analyze.pack(pady=20)

# 第一個數值輸入欄位標籤與輸入框
label1 = tk.Label(left_frame, text="第一個數值：")
label1.pack(pady=(10, 0))
entry1 = tk.Entry(left_frame)
entry1.pack(pady=(0, 10), fill="x")

# 第二個數值輸入欄位標籤與輸入框
label2 = tk.Label(left_frame, text="第二個數值：")
label2.pack(pady=(10, 0))
entry2 = tk.Entry(left_frame)
entry2.pack(pady=(0, 10), fill="x")

# 加法按鈕功能
def do_addition():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 + num2
        text_area.insert(tk.END, f"加法結果：{num1} + {num2} = {result}\n")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數值")

# 加法按鈕
btn_add = tk.Button(left_frame, text="執行加法", command=do_addition, width=20)
btn_add.pack(pady=10)


# 右側文字輸出區塊
right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

text_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Arial", 12))
text_area.pack(expand=True, fill="both")

# 啟動主迴圈
root.mainloop()
