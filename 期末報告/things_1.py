import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import os

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
    def upload_file(self):
        # 設置檔案選擇對話框，確保 CSV 和 Excel 檔案可見
        filetypes = [("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            try:
                # 確保路徑格式正確
                filepath = os.path.normpath(filepath)
                self.output_text.delete(1.0, tk.END)  # 清空輸出區域
                
                if filepath.endswith(".csv"):
                    # 嘗試以不同編碼讀取 CSV
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
                elif filepath.endswith((".xlsx", ".xls")):
                    self.data = pd.read_excel(filepath)
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
                self.output_text.insert(tk.END, f"各欄位缺失值數量：\n{missing_values.to_string()}\n")
                if missing_values.any():
                    self.output_text.insert(tk.END, "\n檢測到缺失值，請在數據解碼中處理。\n")
                else:
                    self.output_text.insert(tk.END, "\n資料中沒有缺失值。\n")
                
                # 啟用解碼按鈕
                self.decode_button.config(state='normal')
            except Exception as e:
                messagebox.showerror("錯誤", f"無法讀取檔案: {str(e)}")
                self.data = None  # 重置數據
        else:
            messagebox.showwarning("警告", "未選擇任何檔案")
    def decode_data(self):
        if self.data is not None:
            try:
                # 清空輸出區域
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "=== 數據解碼處理 ===\n")
                
                # 1. 移除不必要的欄位（假設欄位名稱可能包含 RowNumber, CustomerId, Surname）
                columns_to_drop = [col for col in ['RowNumber', 'CustomerId', 'Surname'] if col in self.data.columns]
                if columns_to_drop:
                    self.data = self.data.drop(columns_to_drop, axis=1)
                    self.output_text.insert(tk.END, f"已移除欄位：{', '.join(columns_to_drop)}\n")
                
                # 2. 處理缺失值
                missing_values = self.data.isnull().sum()
                if missing_values.any():
                    self.output_text.insert(tk.END, "\n處理缺失值：\n")
                    for column in self.data.columns:
                        if missing_values[column] > 0:
                            if self.data[column].dtype in ['int64', 'float64']:  # 數值型欄位
                                median_value = self.data[column].median()
                                self.data[column] = self.data[column].fillna(median_value)
                                self.output_text.insert(tk.END, f"欄位 '{column}'（數值型）：以中位數 {median_value} 填補\n")
                            else:  # 類別型欄位
                                mode_value = self.data[column].mode()[0]
                                self.data[column] = self.data[column].fillna(mode_value)
                                self.output_text.insert(tk.END, f"欄位 '{column}'（類別型）：以眾數 {mode_value} 填補\n")
                    self.output_text.insert(tk.END, "\n缺失值填補後：\n")
                    self.output_text.insert(tk.END, f"{self.data.isnull().sum().to_string()}\n")
                else:
                    self.output_text.insert(tk.END, "\n無缺失值需要處理。\n")
                
                # 3. 類別特徵轉換
                self.output_text.insert(tk.END, "\n=== 類別特徵轉換 ===\n")
                categorical_columns = self.data.select_dtypes(include=['object']).columns
                if len(categorical_columns) > 0:
                    for column in categorical_columns:
                        if self.data[column].nunique() <= 2:  # 二元類別用 Label Encoding
                            le = LabelEncoder()
                            self.data[column] = le.fit_transform(self.data[column])
                            self.output_text.insert(tk.END, f"欄位 '{column}'：應用 Label Encoding\n")
                        else:  # 多類別用 One-Hot Encoding
                            ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
                            encoded = ohe.fit_transform(self.data[[column]])
                            encoded_df = pd.DataFrame(encoded, columns=ohe.get_feature_names_out([column]), index=self.data.index)
                            self.data = pd.concat([self.data.drop(column, axis=1), encoded_df], axis=1)
                            self.output_text.insert(tk.END, f"欄位 '{column}'：應用 One-Hot Encoding\n")
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
            except Exception as e:
                messagebox.showerror("錯誤", f"數據解碼失敗: {e}")
        else:
            messagebox.showwarning("警告", "請先上傳資料")

    def run_decision_tree(self):
            self.output_text.insert(tk.END, "執行決策樹模型訓練...（尚未實作）\n")

    def run_random_forest(self):
            self.output_text.insert(tk.END, "執行隨機森林模型訓練...（尚未實作）\n")

    def run_svm(self):
            self.output_text.insert(tk.END, "執行SVM模型訓練...（尚未實作）\n")

    def run_svm_tuned(self):
            self.output_text.insert(tk.END, "執行SVM（調參）模型訓練...（尚未實作）\n")

    def show_results(self):
            self.output_text.insert(tk.END, "顯示分析結果...（此功能可接入圖表顯示或表格）\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankChurnApp(root)
    root.mainloop()
