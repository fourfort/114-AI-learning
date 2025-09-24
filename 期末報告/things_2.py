import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import tree
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import plot_tree
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from matplotlib.colors import ListedColormap
import numpy as np

class BankChurnApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人工智慧銀行客戶流失分析檢測系統")
        self.root.geometry("1000x600")

        # 左側按鈕區
        self.left_frame = tk.Frame(self.root, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 檔案上傳按鈕
        self.upload_button = tk.Button(self.left_frame, text="分析數據檔案上傳", command=self.upload_file)
        self.upload_button.pack(pady=10, fill=tk.X)

        # 解碼按鈕（初始禁用）
        self.decode_button = tk.Button(self.left_frame, text="數據檔案解碼", command=self.decode_data, state='disabled')
        self.decode_button.pack(pady=10, fill=tk.X)

        # 數據分析按鈕（初始禁用）
        self.analysis_button = tk.Menubutton(self.left_frame, text="數據分析", relief=tk.RAISED, state='disabled')
        self.analysis_menu = tk.Menu(self.analysis_button, tearoff=0)
        self.analysis_menu.add_command(label="演算法分析（決策樹）", command=self.run_decision_tree)
        self.analysis_menu.add_command(label="演算法分析（隨機森林）", command=self.run_random_forest)
        self.analysis_menu.add_command(label="演算法分析（SVM）", command=self.run_svm)
        self.analysis_menu.add_command(label="演算法分析（SVM（調參））", command=self.run_svm_tuned)
        self.analysis_button.configure(menu=self.analysis_menu)
        self.analysis_button.pack(pady=10, fill=tk.X)

        # 分析結果按鈕（初始禁用）
        self.result_button = tk.Button(self.left_frame, text="分析結果", command=self.show_results, state='disabled')
        self.result_button.pack(pady=10, fill=tk.X)

        # 右側輸出區
        self.output_text = tk.Text(self.root, wrap=tk.WORD)
        self.output_text.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.data = None  # 用來儲存上傳的資料
        self.missing_columns = None  # 儲存有缺失值的欄位
        self.categorical_columns = None  # 儲存類別型欄位

    def upload_file(self):
        filetypes = [
            ("All files", "*.*"),
            ("CSV files", "*.csv;*.CSV"),
            ("Excel files", "*.xlsx;*.XLSX;*.xls;*.XLS")
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes, defaultextension="*.*")
        if filepath:
            try:
                filepath = os.path.normpath(filepath)
                self.output_text.delete(1.0, tk.END)  # 清空輸出區域
                
                if filepath.lower().endswith((".csv", ".CSV")):
                    encodings = ['utf-8', 'gbk', 'latin1']
                    self.data = None
                    for encoding in encodings:
                        try:
                            self.data = pd.read_csv(filepath, encoding=encoding)
                            self.output_text.insert(tk.END, f"成功以 {encoding} 編碼讀取 CSV 檔案\n")
                            break
                        except UnicodeDecodeError:
                            continue
                    if self.data is None:
                        raise ValueError("無法以支援的編碼（utf-8, gbk, latin1）讀取 CSV 檔案")
                elif filepath.lower().endswith((".xlsx", ".XLSX", ".xls", ".XLS")):
                    self.data = pd.read_excel(filepath, engine='openpyxl')
                    self.output_text.insert(tk.END, f"成功讀取 Excel 檔案\n")
                else:
                    raise ValueError("不支援的檔案格式，請選擇 .csv 或 .xlsx/.xls 檔案")
                
                # 顯示檔案資訊
                self.output_text.insert(tk.END, f"檔案上傳成功：{filepath}\n\n")
                self.output_text.insert(tk.END, "=== 數據概述 ===\n")
                self.output_text.insert(tk.END, f"欄位名稱：{', '.join(self.data.columns)}\n")
                self.output_text.insert(tk.END, f"數據總筆數：{len(self.data)}\n\n")
                
                # 顯示前5行數據
                self.output_text.insert(tk.END, "前5行數據：\n")
                self.output_text.insert(tk.END, f"{self.data.head().to_string()}\n\n")
                
                # 檢查缺失值
                self.output_text.insert(tk.END, "=== 缺失值檢查 ===\n")
                missing_values = self.data.isnull().sum()
                self.missing_columns = missing_values[missing_values > 0].index.tolist()
                self.output_text.insert(tk.END, f"各欄位缺失值數量：\n{missing_values.to_string()}\n")
                if missing_values.any():
                    self.output_text.insert(tk.END, f"\n檢測到缺失值的欄位：{', '.join(self.missing_columns)}\n")
                else:
                    self.output_text.insert(tk.END, "\n資料中沒有缺失值。\n")
                
                # 識別類別型欄位
                self.categorical_columns = self.data.select_dtypes(include=['object']).columns.tolist()
                self.output_text.insert(tk.END, "\n=== 類別型欄位 ===\n")
                if self.categorical_columns:
                    self.output_text.insert(tk.END, f"類別型欄位：{', '.join(self.categorical_columns)}\n")
                else:
                    self.output_text.insert(tk.END, "無類別型欄位。\n")
                
                # 啟用解碼按鈕
                self.decode_button.config(state='normal')
            except Exception as e:
                messagebox.showerror("錯誤", f"無法讀取檔案: {str(e)}")
                self.data = None
                self.missing_columns = None
                self.categorical_columns = None
        else:
            messagebox.showwarning("警告", "未選擇任何檔案")

    def decode_data(self):
        if self.data is not None:
            # 創建客製化選擇窗口
            self.create_customization_window()
        else:
            messagebox.showwarning("警告", "請先上傳資料")

    def create_customization_window(self):
        # 創建新窗口
        custom_window = tk.Toplevel(self.root)
        custom_window.title("客製化數據處理選項")
        custom_window.geometry("600x600")

        # 欄位刪除選項
        tk.Label(custom_window, text="選擇要刪除的欄位", font=("Arial", 12, "bold")).pack(pady=10)
        frame = tk.Frame(custom_window)
        frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame, text="刪除欄位數量：").pack(side=tk.LEFT)
        self.delete_count = tk.StringVar(value="0")
        ttk.Combobox(frame, textvariable=self.delete_count, values=[str(i) for i in range(len(self.data.columns) + 1)], state="readonly").pack(side=tk.LEFT)
        tk.Button(frame, text="選擇欄位", command=lambda: self.select_columns_to_delete(custom_window)).pack(side=tk.LEFT, padx=10)
        self.delete_columns = []

        # 缺失值處理選項
        tk.Label(custom_window, text="選擇缺失值處理方式", font=("Arial", 12, "bold")).pack(pady=10)
        self.missing_value_choices = {}
        for col in self.missing_columns:
            frame = tk.Frame(custom_window)
            frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(frame, text=f"欄位 '{col}'（{'數值型' if self.data[col].dtype in ['int64', 'float64'] else '類別型'}）：").pack(side=tk.LEFT)
            choice = tk.StringVar(value="中位數" if self.data[col].dtype in ['int64', 'float64'] else "眾數")
            self.missing_value_choices[col] = choice
            ttk.Combobox(frame, textvariable=choice, values=["中位數", "眾數", "保留原本數值"], state="readonly").pack(side=tk.LEFT)
            tk.Label(frame, text="（建議：數值型用中位數，類別型用眾數，保留適用於分析缺失模式）").pack(side=tk.LEFT)

        # 類別特徵轉換選項
        tk.Label(custom_window, text="選擇類別特徵轉換方式", font=("Arial", 12, "bold")).pack(pady=10)
        self.categorical_choices = {}
        for col in self.categorical_columns:
            frame = tk.Frame(custom_window)
            frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(frame, text=f"欄位 '{col}'（唯一值數：{self.data[col].nunique()}）：").pack(side=tk.LEFT)
            choice = tk.StringVar(value="Label Encoding" if self.data[col].nunique() <= 2 else "One-Hot Encoding")
            self.categorical_choices[col] = choice
            ttk.Combobox(frame, textvariable=choice, values=["Label Encoding", "One-Hot Encoding"], state="readonly").pack(side=tk.LEFT)
            tk.Label(frame, text="（建議：2個類別用 Label Encoding，多類別用 One-Hot Encoding）").pack(side=tk.LEFT)

        # 確認按鈕
        tk.Button(custom_window, text="確認並解碼", command=lambda: self.apply_custom_decoding(custom_window)).pack(pady=20)
    def select_columns_to_delete(self, parent_window):
        # 創建欄位選擇窗口
        delete_window = tk.Toplevel(parent_window)
        delete_window.title("選擇要刪除的欄位")
        delete_window.geometry("400x400")

        count = int(self.delete_count.get())
        if count == 0:
            delete_window.destroy()
            return

        tk.Label(delete_window, text=f"請選擇 {count} 個欄位要刪除").pack(pady=10)
        self.delete_selections = []
        for _ in range(count):
            frame = tk.Frame(delete_window)
            frame.pack(fill=tk.X, padx=10, pady=5)
            var = tk.StringVar()
            ttk.Combobox(frame, textvariable=var, values=list(self.data.columns), state="readonly").pack(side=tk.LEFT)
            self.delete_selections.append(var)

        tk.Button(delete_window, text="確認", command=lambda: [self.delete_columns.extend([var.get() for var in self.delete_selections if var.get()]), delete_window.destroy()]).pack(pady=20)

    def apply_custom_decoding(self, custom_window):
        try:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=== 數據解碼處理 ===\n")
            
            # 1. 刪除選擇的欄位
            if self.delete_columns:
                unique_columns = list(dict.fromkeys(self.delete_columns))  # 移除重複
                valid_columns = [col for col in unique_columns if col in self.data.columns]
                if valid_columns:
                    self.data = self.data.drop(valid_columns, axis=1)
                    self.output_text.insert(tk.END, f"已刪除欄位：{', '.join(valid_columns)}\n")
                    # 更新缺失值和類別欄位列表
                    self.missing_columns = [col for col in self.missing_columns if col not in valid_columns]
                    self.categorical_columns = [col for col in self.categorical_columns if col not in valid_columns]
            
            # 2. 處理缺失值
            if self.missing_columns:
                self.output_text.insert(tk.END, "\n處理缺失值：\n")
                for col in self.missing_columns:
                    choice = self.missing_value_choices.get(col, tk.StringVar(value="中位數" if self.data[col].dtype in ['int64', 'float64'] else "眾數")).get()
                    if choice == "中位數":
                        median_value = self.data[col].median()
                        self.data[col] = self.data[col].fillna(median_value)
                        self.output_text.insert(tk.END, f"欄位 '{col}'：以中位數 {median_value} 填補\n")
                    elif choice == "眾數":
                        mode_value = self.data[col].mode()[0]
                        self.data[col] = self.data[col].fillna(mode_value)
                        self.output_text.insert(tk.END, f"欄位 '{col}'：以眾數 {mode_value} 填補\n")
                    elif choice == "保留原本數值":
                        self.output_text.insert(tk.END, f"欄位 '{col}'：保留缺失值未處理\n")
                self.output_text.insert(tk.END, "\n缺失值處理後：\n")
                self.output_text.insert(tk.END, f"{self.data.isnull().sum().to_string()}\n")
            else:
                self.output_text.insert(tk.END, "\n無缺失值需要處理。\n")
            
            # 3. 類別特徵轉換
            self.output_text.insert(tk.END, "\n=== 類別特徵轉換 ===\n")
            if self.categorical_columns:
                for col in self.categorical_columns[:]:  # 使用切片複製以避免修改迴圈中的列表
                    choice = self.categorical_choices.get(col, tk.StringVar(value="Label Encoding" if self.data[col].nunique() <= 2 else "One-Hot Encoding")).get()
                    if choice == "Label Encoding":
                        le = LabelEncoder()
                        self.data[col] = le.fit_transform(self.data[col])
                        self.output_text.insert(tk.END, f"欄位 '{col}'：應用 Label Encoding\n")
                    elif choice == "One-Hot Encoding":
                        ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
                        encoded = ohe.fit_transform(self.data[[col]])
                        encoded_df = pd.DataFrame(encoded, columns=ohe.get_feature_names_out([col]), index=self.data.index)
                        self.data = pd.concat([self.data.drop(col, axis=1), encoded_df], axis=1)
                        self.output_text.insert(tk.END, f"欄位 '{col}'：應用 One-Hot Encoding\n")
                    self.categorical_columns.remove(col)  # 更新類別欄位列表
            else:
                self.output_text.insert(tk.END, "無類別特徵需要轉換。\n")
            
            # 4. 顯示最終數據
            self.output_text.insert(tk.END, "\n=== 解碼後數據概述 ===\n")
            self.output_text.insert(tk.END, f"欄位名稱：{', '.join(self.data.columns)}\n")
            self.output_text.insert(tk.END, f"前5行數據：\n{self.data.head().to_string()}\n")
            self.output_text.insert(tk.END, "\n數據已準備好進行分析！\n")
            
            # 啟用分析和結果按鈕
            self.analysis_button.config(state='normal')
            self.result_button.config(state='normal')
            
            # 關閉客製化窗口
            custom_window.destroy()
        except Exception as e:
            messagebox.showerror("錯誤", f"數據解碼失敗: {str(e)}")

    def ask_target_knowledge(self, algorithm_callback):
        # 詢問使用者是否知道如何選擇目標變數
        knowledge_window = tk.Toplevel(self.root)
        knowledge_window.title("目標變數知識確認")
        knowledge_window.geometry("400x200")

        tk.Label(knowledge_window, text="您知道如何選擇目標變數嗎？", font=("Arial", 12, "bold")).pack(pady=20)
        tk.Button(knowledge_window, text="知道，選擇欄位", command=lambda: [knowledge_window.destroy(), self.select_target_variable(algorithm_callback)]).pack(pady=10)
        tk.Button(knowledge_window, text="不知道，使用預設", command=lambda: [knowledge_window.destroy(), self.set_default_target(algorithm_callback)]).pack(pady=10)

    def select_target_variable(self, algorithm_callback):
        # 創建目標變數選擇窗口
        target_window = tk.Toplevel(self.root)
        target_window.title("選擇目標變數")
        target_window.geometry("400x200")

        tk.Label(target_window, text="請選擇目標變數", font=("Arial", 12, "bold")).pack(pady=10)
        self.target_var = tk.StringVar(value=self.data.columns[-1])  # 預設為最後一欄
        ttk.Combobox(target_window, textvariable=self.target_var, values=list(self.data.columns), state="readonly").pack(pady=10)
        tk.Label(target_window, text="（建議：選擇預測目標，如 'Exited' 或其他分類/回歸欄位）").pack(pady=5)

        tk.Button(target_window, text="確認", command=lambda: [self.set_target_and_run(algorithm_callback, target_window)]).pack(pady=20)
    def set_default_target(self, algorithm_callback):
        # 使用預設目標變數（最後一欄）
        self.target_variable = self.data.columns[-1]
        self.select_split_ratio(algorithm_callback)
    def set_target_and_run(self, algorithm_callback, target_window):
        # 儲存目標變數並執行
        self.target_variable = self.target_var.get()
        target_window.destroy()
        # 選擇資料分割比例
        self.select_split_ratio(algorithm_callback)
    def select_split_ratio(self, algorithm_callback):
        # 創建資料分割比例選擇窗口
        split_window = tk.Toplevel(self.root)
        split_window.title("選擇資料分割比例")
        split_window.geometry("500x300")

        tk.Label(split_window, text="請選擇訓練/測試資料分割比例", font=("Arial", 12, "bold")).pack(pady=10)
        self.split_ratio = tk.StringVar(value="8:2")
        ratios = ["9:1 (0.1)", "8:2 (0.2)", "7:3 (0.3)", "6:4 (0.4)", "5:5 (0.5)"]
        ttk.Combobox(split_window, textvariable=self.split_ratio, values=ratios, state="readonly").pack(pady=10)
        tk.Label(split_window, text="建議比例：\n- 決策樹：8:2\n- 隨機森林：9:1\n- SVM：7:3\n- SVM（調參）：7:3").pack(pady=10)

        tk.Button(split_window, text="確認", command=lambda: [self.set_split_ratio_and_run(algorithm_callback, split_window)]).pack(pady=20)
    def set_split_ratio_and_run(self, algorithm_callback, split_window):
        # 儲存分割比例並執行
        ratio = self.split_ratio.get()
        self.test_size = float(ratio.split('(')[1].strip(')'))
        split_window.destroy()
        algorithm_callback()

    def run_decision_tree(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.ask_target_knowledge(self.run_decision_tree_logic)

    def run_decision_tree_logic(self):
        try:
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=== 決策樹模型訓練 ===\n")
            self.output_text.insert(tk.END, f"目標變數: {self.target_variable}\n")
            self.output_text.insert(tk.END, f"使用演算法: 決策樹\n")

            # 定義特徵與標籤
            features = [col for col in self.data.columns if col != self.target_variable]
            X = self.data[features]
            y = self.data[self.target_variable]

            # 分割資料 (訓練:測試 = 經前者使用者選擇的比例)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
            self.output_text.insert(tk.END, f"資料分割比例: 訓練 {int((1-self.test_size)*100)}% / 測試 {int(self.test_size*100)}%（建議：8:2 為穩健評估比例）\n")
            self.output_text.insert(tk.END, f"訓練資料筆數: {X_train.shape[0]}\n")
            self.output_text.insert(tk.END, f"測試資料筆數: {X_test.shape[0]}\n\n")

            # 訓練決策樹模型 (最大深度為5)
            dt_classifier = DecisionTreeClassifier(max_depth=5, random_state=42)
            dt_classifier.fit(X_train, y_train)
            y_pred = dt_classifier.predict(X_test)

            # 模型評估
            self.output_text.insert(tk.END, "--- 模型評估 ---\n")
            cm = confusion_matrix(y_test, y_pred)
            self.output_text.insert(tk.END, f"混淆矩陣:\n{cm}\n\n")
            self.output_text.insert(tk.END, f"準確率: {accuracy_score(y_test, y_pred):.4f}\n")
            self.output_text.insert(tk.END, f"精確率: {precision_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"召回率: {recall_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"F1 分數: {f1_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"\n分類報告:\n{classification_report(y_test, y_pred)}\n")

            # 創建圖形窗口
            graph_window = tk.Toplevel(self.root)
            graph_window.title("決策樹模型視覺化")
            graph_window.geometry("800x600")

            # 混淆矩陣圖
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
            ax1.set_xlabel("預測值")
            ax1.set_ylabel("真實值")
            ax1.set_title("混淆矩陣")

            # 決策樹圖
            tree.plot_tree(dt_classifier, feature_names=features, class_names=['0', '1'], filled=True, ax=ax2)
            ax2.set_title("決策樹 (max_depth=5)")

            # 將圖形嵌入 Tkinter 窗口
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            self.output_text.insert(tk.END, "已顯示混淆矩陣與決策樹圖形\n")
        except Exception as e:
            messagebox.showerror("錯誤", f"決策樹訓練失敗: {str(e)}")

    def run_random_forest(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.ask_target_knowledge(self.run_random_forest_logic)

    def run_random_forest_logic(self):
        try:
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=== 隨機森林模型訓練 ===\n")
            self.output_text.insert(tk.END, f"目標變數: {self.target_variable}\n")
            self.output_text.insert(tk.END, f"使用演算法: 隨機森林\n")

            # 定義特徵與標籤
            features = [col for col in self.data.columns if col != self.target_variable]
            X = self.data[features]
            y = self.data[self.target_variable]

            # 分割資料
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
            self.output_text.insert(tk.END, f"資料分割比例: 訓練 {int((1-self.test_size)*100)}% / 測試 {int(self.test_size*100)}%（建議：隨機森林適用 9:1）\n")
            self.output_text.insert(tk.END, f"訓練資料筆數: {X_train.shape[0]}\n")
            self.output_text.insert(tk.END, f"測試資料筆數: {X_test.shape[0]}\n\n")

            # 隨機森林初始化與訓練
            rf_classifier = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
            self.output_text.insert(tk.END, "隨機森林模型參數：\n")
            self.output_text.insert(tk.END, f"{rf_classifier.get_params()}\n\n")
            rf_classifier.fit(X_train, y_train)

            # 模型預測
            y_pred = rf_classifier.predict(X_test)

            # 模型評估
            self.output_text.insert(tk.END, "--- 模型評估 ---\n")
            cm = confusion_matrix(y_test, y_pred)
            self.output_text.insert(tk.END, f"混淆矩陣:\n{cm}\n\n")
            self.output_text.insert(tk.END, f"準確率: {accuracy_score(y_test, y_pred):.4f}\n")
            self.output_text.insert(tk.END, f"精確率: {precision_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"召回率: {recall_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"F1 分數: {f1_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"\n分類報告:\n{classification_report(y_test, y_pred)}\n")

            # 創建圖形窗口
            graph_window = tk.Toplevel(self.root)
            graph_window.title("隨機森林模型視覺化")
            graph_window.geometry("1200x600")

            # 混淆矩陣圖
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
            ax1.set_xlabel("預測值")
            ax1.set_ylabel("真實值")
            ax1.set_title("混淆矩陣")

            # 隨機森林中第一棵樹
            plot_tree(rf_classifier.estimators_[0], feature_names=features, class_names=['Not Churned', 'Churned'], filled=True, rounded=True, ax=ax2)
            ax2.set_title("隨機森林第一棵樹 (max_depth=5)")

            # 將圖形嵌入 Tkinter 窗口
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            self.output_text.insert(tk.END, "已顯示混淆矩陣與隨機森林第一棵樹圖形\n")
        except Exception as e:
            messagebox.showerror("錯誤", f"隨機森林訓練失敗: {str(e)}")

    def run_svm(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.ask_target_knowledge(self.run_svm_logic)

    def run_svm_logic(self):
        try:
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=== SVM 模型訓練 ===\n")
            self.output_text.insert(tk.END, f"目標變數: {self.target_variable}\n")
            self.output_text.insert(tk.END, f"使用演算法: SVM (未調參)\n")

            # 定義特徵與標籤
            features = [col for col in self.data.columns if col != self.target_variable]
            X = self.data[features]
            y = self.data[self.target_variable]

            # 分割資料
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
            self.output_text.insert(tk.END, f"資料分割比例: 訓練 {int((1-self.test_size)*100)}% / 測試 {int(self.test_size*100)}%（建議：SVM 適用 7:3）\n")
            self.output_text.insert(tk.END, f"訓練資料筆數: {X_train.shape[0]}\n")
            self.output_text.insert(tk.END, f"測試資料筆數: {X_test.shape[0]}\n\n")

            # 標準化特徵
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # SVM 初始化與訓練
            svm_model = SVC(kernel='rbf', probability=True, random_state=42)
            self.output_text.insert(tk.END, "SVM 模型參數：\n")
            self.output_text.insert(tk.END, f"{svm_model.get_params()}\n\n")
            svm_model.fit(X_train_scaled, y_train)

            # 模型預測
            y_pred = svm_model.predict(X_test_scaled)

            # 模型評估
            self.output_text.insert(tk.END, "--- 模型評估 ---\n")
            cm = confusion_matrix(y_test, y_pred)
            self.output_text.insert(tk.END, f"混淆矩陣:\n{cm}\n\n")
            self.output_text.insert(tk.END, f"準確率: {accuracy_score(y_test, y_pred):.4f}\n")
            self.output_text.insert(tk.END, f"精確率: {precision_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"召回率: {recall_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"F1 分數: {f1_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"\n分類報告:\n{classification_report(y_test, y_pred)}\n")

            # 創建圖形窗口
            graph_window = tk.Toplevel(self.root)
            graph_window.title("SVM 模型視覺化")
            graph_window.geometry("1200x600")

            # 混淆矩陣圖
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
            ax1.set_xlabel("預測值")
            ax1.set_ylabel("真實值")
            ax1.set_title("混淆矩陣")

            # PCA 降維與決策邊界視覺化
            pca = PCA(n_components=2)
            X_train_pca = pca.fit_transform(X_train_scaled)
            X_test_pca = pca.transform(X_test_scaled)

            svm_pca = SVC(kernel='rbf', probability=True, random_state=42)
            svm_pca.fit(X_train_pca, y_train)

            x_min, x_max = X_train_pca[:, 0].min() - 1, X_train_pca[:, 0].max() + 1
            y_min, y_max = X_train_pca[:, 1].min() - 1, X_train_pca[:, 1].max() + 1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))
            Z = svm_pca.predict(np.array([xx.ravel(), yy.ravel()]).T)
            Z = Z.reshape(xx.shape)

            ax2.contourf(xx, yy, Z, alpha=0.75, cmap=ListedColormap(('red', 'green')))
            ax2.scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=y_train, edgecolors='k', cmap=ListedColormap(('red', 'green')))
            ax2.set_title('SVM 決策邊界 (PCA 降維空間)')
            ax2.set_xlabel('主成分 1')
            ax2.set_ylabel('主成分 2')

            # 將圖形嵌入 Tkinter 窗口
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            self.output_text.insert(tk.END, "已顯示混淆矩陣與 SVM 決策邊界圖形（PCA 降維）\n")
        except Exception as e:
            messagebox.showerror("錯誤", f"SVM 訓練失敗: {str(e)}")
            self.output_text.insert(tk.END, "執行SVM模型訓練...（尚未實作）\n")

    def run_svm_tuned(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.ask_target_knowledge(self.run_svm_tuned_logic)

    def run_svm_tuned_logic(self):
        try:
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=== SVM（調參）模型訓練 ===\n")
            self.output_text.insert(tk.END, f"目標變數: {self.target_variable}\n")
            self.output_text.insert(tk.END, f"使用演算法: SVM (調參, C=1, gamma=0.1)\n")

            # 定義特徵與標籤
            features = [col for col in self.data.columns if col != self.target_variable]
            X = self.data[features]
            y = self.data[self.target_variable]

            # 分割資料
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
            self.output_text.insert(tk.END, f"資料分割比例: 訓練 {int((1-self.test_size)*100)}% / 測試 {int(self.test_size*100)}%（建議：SVM（調參）適用 7:3）\n")
            self.output_text.insert(tk.END, f"訓練資料筆數: {X_train.shape[0]}\n")
            self.output_text.insert(tk.END, f"測試資料筆數: {X_test.shape[0]}\n\n")

            # 標準化特徵
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # SVM（調參）初始化與訓練
            svm_model = SVC(kernel='rbf', C=1, gamma=0.1, probability=True, random_state=42)
            self.output_text.insert(tk.END, "SVM（調參）模型參數：\n")
            self.output_text.insert(tk.END, f"{svm_model.get_params()}\n\n")
            svm_model.fit(X_train_scaled, y_train)

            # 模型預測
            y_pred = svm_model.predict(X_test_scaled)

            # 模型評估
            self.output_text.insert(tk.END, "--- 模型評估 ---\n")
            cm = confusion_matrix(y_test, y_pred)
            self.output_text.insert(tk.END, f"混淆矩陣:\n{cm}\n\n")
            self.output_text.insert(tk.END, f"準確率: {accuracy_score(y_test, y_pred):.4f}\n")
            self.output_text.insert(tk.END, f"精確率: {precision_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"召回率: {recall_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"F1 分數: {f1_score(y_test, y_pred, average='binary'):.4f}\n")
            self.output_text.insert(tk.END, f"\n分類報告:\n{classification_report(y_test, y_pred)}\n")

            # 創建圖形窗口
            graph_window = tk.Toplevel(self.root)
            graph_window.title("SVM（調參）模型視覺化")
            graph_window.geometry("1200x600")

            # 混淆矩陣圖
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1)
            ax1.set_xlabel("預測值")
            ax1.set_ylabel("真實值")
            ax1.set_title("混淆矩陣")

            # PCA 降維與決策邊界視覺化
            pca = PCA(n_components=2)
            X_train_pca = pca.fit_transform(X_train_scaled)
            X_test_pca = pca.transform(X_test_scaled)

            svm_pca = SVC(kernel='rbf', C=1, gamma=0.1, probability=True, random_state=42)
            svm_pca.fit(X_train_pca, y_train)

            x_min, x_max = X_train_pca[:, 0].min() - 1, X_train_pca[:, 0].max() + 1
            y_min, y_max = X_train_pca[:, 1].min() - 1, X_train_pca[:, 1].max() + 1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))
            Z = svm_pca.predict(np.array([xx.ravel(), yy.ravel()]).T)
            Z = Z.reshape(xx.shape)

            ax2.contourf(xx, yy, Z, alpha=0.75, cmap=ListedColormap(('red', 'green')))
            ax2.scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=y_train, edgecolors='k', cmap=ListedColormap(('red', 'green')))
            ax2.set_title('SVM（調參）決策邊界 (PCA 降維空間)')
            ax2.set_xlabel('主成分 1')
            ax2.set_ylabel('主成分 2')

            # 將圖形嵌入 Tkinter 窗口
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            self.output_text.insert(tk.END, "已顯示混淆矩陣與 SVM（調參）決策邊界圖形（PCA 降維後）\n")
        except Exception as e:
            messagebox.showerror("錯誤", f"SVM（調參）訓練失敗: {str(e)}")
    def show_results(self):
        self.output_text.insert(tk.END, "顯示分析結果...（此功能可接入圖表顯示或表格）\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankChurnApp(root)
    root.mainloop()