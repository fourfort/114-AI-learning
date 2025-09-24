import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# 建立主視窗
root = tk.Tk()
root.title("人工智慧數據分析系統")
root.geometry("800x600")

# 左側按鈕區塊
left_frame = tk.Frame(root, width=200)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

# 上傳 Excel 檔案
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
    if file_path:
        text_area.insert(tk.END, f"已選取檔案：{file_path}\n")
        # 這裡可以加入資料讀取的程式，例如 pandas.read_excel()

# 執行決策樹分析
def run_analysis():
    text_area.insert(tk.END, "正在執行決策樹分析...\n")
    # 這裡加入決策樹的分析邏輯
    # 範例：text_area.insert(tk.END, "分析結果：XXX\n")

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
