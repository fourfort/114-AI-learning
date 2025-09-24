import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import pandas as pd

class DataAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人工智慧數據分析系統")
        self.root.geometry("800x500")

        # 儲存上傳的 DataFrame
        self.df = None

        # 左側按鈕區域
        self.left_frame = tk.Frame(self.root, width=150, bg="#f0f0f0")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.upload_button = tk.Button(self.left_frame, text="分析檔案上傳（Excel）", command=self.upload_file)
        self.upload_button.pack(pady=20, padx=10, fill=tk.X)

        self.analyze_button = tk.Button(self.left_frame, text="數據分析（決策樹）", command=self.analyze_data)
        self.analyze_button.pack(pady=20, padx=10, fill=tk.X)

        # 右側輸出區
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.output_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD)
        self.output_text.pack(expand=True, fill=tk.BOTH)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.output_text.insert(tk.END, f"✅ 檔案成功上傳：{file_path}\n")
                self.output_text.insert(tk.END, f"📊 資料筆數：{len(self.df)}，欄位數：{len(self.df.columns)}\n\n")
                self.output_text.insert(tk.END, f"欄位名稱：{list(self.df.columns)}\n\n")
            except Exception as e:
                messagebox.showerror("錯誤", f"檔案上傳失敗：{e}")

    def analyze_data(self):
        if self.df is None:
            messagebox.showwarning("提醒", "請先上傳 Excel 檔案")
            return
        # 這裡可以加入你自訂的決策樹分析邏輯
        self.output_text.insert(tk.END, "📈 開始進行決策樹分析...\n")
        # 示意輸出
        self.output_text.insert(tk.END, f"（此處顯示分析結果...）\n\n")


# 執行主視窗
if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalysisApp(root)
    root.mainloop()
