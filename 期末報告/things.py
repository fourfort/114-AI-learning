import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

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

        # 解碼按鈕
        self.decode_button = tk.Button(self.left_frame, text="數據檔案解碼", command=self.decode_data)
        self.decode_button.pack(pady=10, fill=tk.X)

        # 數據分析按鈕
        self.analysis_button = tk.Menubutton(self.left_frame, text="數據分析", relief=tk.RAISED)
        self.analysis_menu = tk.Menu(self.analysis_button, tearoff=0)
        self.analysis_menu.add_command(label="演算法分析（決策樹）", command=self.run_decision_tree)
        self.analysis_menu.add_command(label="演算法分析（隨機森林）", command=self.run_random_forest)
        self.analysis_menu.add_command(label="演算法分析（SVM）", command=self.run_svm)
        self.analysis_menu.add_command(label="演算法分析（SVM（調參））", command=self.run_svm_tuned)
        self.analysis_button.configure(menu=self.analysis_menu)
        self.analysis_button.pack(pady=10, fill=tk.X)

        # 分析結果按鈕
        self.result_button = tk.Button(self.left_frame, text="分析結果", command=self.show_results)
        self.result_button.pack(pady=10, fill=tk.X)

        # 右側輸出區
        self.output_text = tk.Text(self.root, wrap=tk.WORD)
        self.output_text.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.data = None  # 用來儲存上傳的資料

    def upload_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if filepath:
            try:
                if filepath.endswith(".csv"):
                    self.data = pd.read_csv(filepath)
                else:
                    self.data = pd.read_excel(filepath)
                self.output_text.insert(tk.END, f"檔案上傳成功：{filepath}\n")
            except Exception as e:
                messagebox.showerror("錯誤", f"無法讀取檔案: {e}")

    def decode_data(self):
        if self.data is not None:
            self.output_text.insert(tk.END, "資料解碼完成（此功能可擴充處理資料前處理）\n")
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
