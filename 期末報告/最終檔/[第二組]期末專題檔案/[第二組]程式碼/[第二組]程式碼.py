import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import plot_tree
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from matplotlib.colors import ListedColormap
import numpy as np
from PIL import Image, ImageTk
from tkinter.scrolledtext import ScrolledText

class BankChurnApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # 隱藏主窗口，直到歡迎界面關閉
        self.font_chinese = ('DFKai-SB', 12)
        self.font_english = ('Times New Roman', 12)
        self.current_algorithm = None  # 追蹤最新演算法
        self.inner_frame = None  # 儲存內部框架
        self.graph_window = None  # 儲存圖表窗口
         # 表格樣式
        style = ttk.Style()
        style.configure('oddrow.Treeview', background='#E6E6FA')  # 奇數行紫色
        style.configure('evenrow.Treeview', background='#FFFFFF')  # 偶數行白色

        self.show_welcome_screen()

    def show_welcome_screen(self):
        # 創建歡迎界面
        self.welcome_window = tk.Toplevel(self.root)
        self.welcome_window.title("歡迎")
        self.welcome_window.geometry("1000x600")
        self.welcome_window.configure(bg='#E6E6FA')

        # 創建 Canvas
        self.canvas = tk.Canvas(self.welcome_window, bg='#E6E6FA', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
	# 初始化背景圖片
        self.original_img = None
        img_path = os.path.join(os.path.dirname(__file__), "GUI_picture.jpg")  # ✅ 統一為空格縮排
        try:
            self.original_img = Image.open(img_path).convert('RGBA')  # 確保 RGBA 模式
        except Exception:
            self.canvas.configure(bg='#E6E6FA')

        # 儲存 Canvas 元素 ID
        self.bg_image_id = None
        self.title_text_id = None
        self.subtitle_text_id = None
        self.team_title_id = None
        self.team_member1_id = None
        self.team_member2_id = None
        self.team_member3_id = None
        self.start_button_window = None

        def resize_content(event):
            # 取得當前窗口尺寸
            win_width = event.width
            win_height = event.height

            # 清除舊內容
            self.canvas.delete("all")

            # 縮放背景圖片並應用霧狀效果
            if self.original_img:
                # 保持圖片比例
                img_ratio = self.original_img.width / self.original_img.height
                win_ratio = win_width / win_height
                if img_ratio > win_ratio:
                    new_width = int(win_height * img_ratio)
                    new_height = win_height
                else:
                    new_width = win_width
                    new_height = int(win_width / img_ratio)
                resized_img = self.original_img.resize((new_width, new_height), Image.LANCZOS)

                # 創建霧狀效果（透明度 0.3）
                foggy_img = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 76))  # 白色，30% 不透明
                blended_img = Image.blend(resized_img, foggy_img, 0.7)  # 混合圖片
                self.bg_photo = ImageTk.PhotoImage(blended_img)
                self.bg_image_id = self.canvas.create_image(win_width / 2, win_height / 2, image=self.bg_photo, anchor='center')
            else:
                self.canvas.configure(bg='#E6E6FA')

            # 動態計算文字和按鈕位置
            title_y = win_height * 0.25
            subtitle_y = win_height * 0.35
            team_y_start = win_height * 0.45
            button_y = win_height * 0.80  # 按鈕下移

            # 大標題
            title_font_size = max(20, int(win_width * 0.036))  # 約 36
            self.title_text_id = self.canvas.create_text(
                win_width / 2, title_y,
                text="人工智慧銀行客戶流失分析檢測系統",
                font=('DFKai-SB', title_font_size, 'bold'),
                fill='black',
                anchor='center'
            )

            # 小標題
            subtitle_font_size = max(12, int(win_width * 0.024))  # 約 24
            self.subtitle_text_id = self.canvas.create_text(
                win_width / 2, subtitle_y,
                text="商業人工智慧導論期末成果發表",
                font=('DFKai-SB', subtitle_font_size, 'bold'),
                fill='black',
                anchor='center'
            )

            # 團隊成員（居中）
            team_font_size = max(12, int(win_width * 0.020))  # 約 20
            self.team_title_id = self.canvas.create_text(
                win_width / 2, team_y_start,
                text="團隊成員：",
                font=('DFKai-SB', team_font_size, 'bold'),
                fill='black',
                anchor='center'
            )
            self.team_member1_id = self.canvas.create_text(
                win_width / 2, team_y_start + team_font_size * 2,
                text="B1011035 高鈿傑",
                font=('DFKai-SB', team_font_size),
                fill='black',
                anchor='center'
            )
            self.team_member2_id = self.canvas.create_text(
                win_width / 2, team_y_start + team_font_size * 4,
                text="B1112204 何虹儀",
                font=('DFKai-SB', team_font_size),
                fill='black',
                anchor='center'
            )
            self.team_member3_id = self.canvas.create_text(
                win_width / 2, team_y_start + team_font_size * 6,
                text="B1141065 陳昱安",
                font=('DFKai-SB', team_font_size),
                fill='black',
                anchor='center'
            )

            # 開始按鈕
            button_font_size = max(12, int(win_width * 0.020))  # 約 20
            start_button = tk.Button(
                self.welcome_window,
                text="開始",
                command=self.start_main_screen,
                font=('DFKai-SB', button_font_size),
                bg='#D8BFD8',
                fg='black',
                width=12
            )
            self.start_button_window = self.canvas.create_window(
                win_width / 2, button_y,
                window=start_button,
                anchor='center'
            )

        # 綁定窗口大小變化事件
        self.canvas.bind('<Configure>', resize_content)

        # 初始繪製
        self.welcome_window.update()
        class CustomEvent:
            def __init__(self, width, height):
                self.width = width
                self.height = height
        resize_content(CustomEvent(width=self.canvas.winfo_width(), height=self.canvas.winfo_height()))
    
    def start_main_screen(self):
        # 關閉歡迎界面
        self.welcome_window.destroy()
        # 顯示主窗口
        self.root.deiconify()
        self.root.title("人工智慧銀行客戶流失分析檢測系統")
        self.root.geometry("1200x800")
        self.root.configure(bg='#E6E6FA')

        # 左側按鈕區
        self.left_frame = tk.Frame(self.root, width=200, bg='#E6E6FA')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.intro_button = tk.Button(self.left_frame, text="系統介紹", command=self.show_system_intro, font=self.font_chinese, bg='#D8BFD8', fg='black')
        self.intro_button.pack(pady=10, fill=tk.X)
        self.upload_button = tk.Button(self.left_frame, text="分析數據檔案上傳", command=self.upload_file, font=self.font_chinese, bg='#D8BFD8', fg='black')
        self.upload_button.pack(pady=10, fill=tk.X)
        self.decode_button = tk.Button(self.left_frame, text="數據檔案解碼", command=self.decode_data, state='disabled', font=self.font_chinese, bg='#D8BFD8', fg='black')
        self.decode_button.pack(pady=10, fill=tk.X)
        self.analysis_button = tk.Menubutton(self.left_frame, text="數據分析", relief=tk.RAISED, state='disabled', font=self.font_chinese, bg='#D8BFD8', fg='black')
        self.analysis_menu = tk.Menu(self.analysis_button, tearoff=0, font=self.font_chinese)
        self.analysis_menu.add_command(label="演算法分析（決策樹）", command=self.run_decision_tree)
        self.analysis_menu.add_command(label="演算法分析（隨機森林）", command=self.run_random_forest)
        self.analysis_menu.add_command(label="演算法分析（SVM）", command=self.run_svm)
        self.analysis_menu.add_command(label="演算法分析（SVM（調參））", command=self.run_svm_tuned)
        self.analysis_menu.add_command(label="分析全部演算法", command=self.run_all_algorithms)
        self.analysis_button.configure(menu=self.analysis_menu)
        self.analysis_button.pack(pady=10, fill=tk.X)
        self.result_button = tk.Button(self.left_frame, text="分析結果", command=self.show_results, state='disabled', font=self.font_chinese, bg='#D8BFD8', fg='black')
        self.result_button.pack(pady=10, fill=tk.X)
        self.team_button = tk.Button(self.left_frame, text="製作團隊", command=self.show_team_info, font=self.font_chinese, bg='#D8BFD8', fg='black')
        self.team_button.pack(pady=10, fill=tk.X)

        # 右側輸出區
        self.output_frame = tk.Frame(self.root, bg='#F5F5F5')
        self.output_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 創建內部框架（居中）
        self.inner_frame = tk.Frame(self.output_frame, bg='white')
        self.inner_frame.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.95, anchor='center')

        # 文字輸出（使用 ScrolledText 提供垂直和水平捲動條）
        output_font = ('DFKai-SB', 16)
        self.output_text = ScrolledText(self.inner_frame, wrap=tk.NONE, font=output_font, bg='white', fg='black', borderwidth=0, padx=10, pady=5, width=100, height=30)
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 配置水平捲動條
        h_scrollbar = ttk.Scrollbar(self.inner_frame, orient=tk.HORIZONTAL, command=self.output_text.xview)
        self.output_text.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 表格區域（備用）
        self.table_frame = tk.Frame(self.inner_frame, bg='white')
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 滑鼠滾輪綁定
        def on_mousewheel(event):
            if event.delta:
                self.output_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                self.output_text.yview_scroll(-1, "units")
            elif event.num == 5:
                self.output_text.yview_scroll(1, "units")

        def on_shift_mousewheel(event):
            if event.delta:
                self.output_text.xview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                self.output_text.xview_scroll(-1, "units")
            elif event.num == 5:
                self.output_text.xview_scroll(1, "units")

        self.output_text.bind("<MouseWheel>", on_mousewheel)
        self.output_text.bind("<Button-4>", on_mousewheel)
        self.output_text.bind("<Button-5>", on_mousewheel)
        self.output_text.bind("<Shift-MouseWheel>", on_shift_mousewheel)
        self.output_text.bind("<Shift-Button-4>", on_shift_mousewheel)
        self.output_text.bind("<Shift-Button-5>", on_shift_mousewheel)

        self.data = None
        self.missing_columns = None
        self.categorical_columns = None
        self.target_variable = None
        self.results = {}
        self.current_algorithm = None
        self.graph_window = None

        # 顯示歡迎詞
        welcome_message = """歡迎各位尊貴的使用者蒞臨本銀行客戶流失分析檢測系統，\n願本系統助您洞悉客戶動向，精準施策，共創卓越未來！\n"""
        self.output_text.insert(tk.END, welcome_message)

    def clear_table_frame(self):
        """清空文字和表格區域的所有內容"""
        self.output_text.delete(1.0, tk.END)
        for widget in self.output_text.winfo_children():
            widget.destroy()
        for widget in self.table_frame.winfo_children():
            widget.pack_forget()
            widget.destroy()
        self.table_frame.pack_forget()

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
                if not os.path.exists(filepath):
                    raise FileNotFoundError(f"檔案不存在：{filepath}")

                self.clear_table_frame()

                # 讀取檔案
                if filepath.lower().endswith((".csv", ".CSV")):
                    encodings = ['utf-8', 'gbk', 'latin1', 'utf-16', 'big5']
                    self.data = None
                    for encoding in encodings:
                        try:
                            self.data = pd.read_csv(filepath, encoding=encoding)
                            self.output_text.insert(tk.END, f"成功以 {encoding} 編碼讀取 CSV 檔案\n")
                            break
                        except UnicodeDecodeError:
                            continue
                    if self.data is None:
                        raise ValueError("無法以支援的編碼（utf-8, gbk, latin1, utf-16, big5）讀取 CSV 檔案")
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

                # 前5行數據
                self.output_text.insert(tk.END, "前5行數據：\n\n")
                tree = ttk.Treeview(self.inner_frame, columns=list(self.data.columns), show='headings', height=5)
                total_width = 0
                for col in self.data.columns:
                    col_width = max(80, min(150, len(str(col)) * 8 + 20))
                    tree.heading(col, text=col)
                    tree.column(col, width=col_width, anchor='w')
                    total_width += col_width
                # 限制表格總寬
                if total_width > 1200:
                    for col in self.data.columns:
                        tree.column(col, width=70)
                for idx, row in self.data.head().iterrows():
                    tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
                    tree.insert('', tk.END, values=[str(val) for val in row], tags=tags)
                self.output_text.window_create(tk.END, window=tree, padx=10, pady=5)
                self.output_text.insert(tk.END, "\n")

                # 檢查缺失值
                self.output_text.insert(tk.END, "\n=== 缺失值檢查 ===\n")
                missing_values = self.data.isnull().sum()
                self.missing_columns = missing_values[missing_values > 0].index.tolist()

                # 缺失值表格
                tree_missing = ttk.Treeview(self.inner_frame, columns=['欄位', '缺失值數量'], show='headings', height=len(missing_values))
                tree_missing.heading('欄位', text='欄位')
                tree_missing.heading('缺失值數量', text='缺失值數量')
                tree_missing.column('欄位', width=150, anchor='w')
                tree_missing.column('缺失值數量', width=100, anchor='w')
                for idx, (col, count) in enumerate(missing_values.items()):
                    tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
                    tree_missing.insert('', tk.END, values=[col, count], tags=tags)
                self.output_text.window_create(tk.END, window=tree_missing, padx=10, pady=5)
                self.output_text.insert(tk.END, "\n")

                # 缺失值文字
                if missing_values.any():
                    self.output_text.insert(tk.END, f"檢測到缺失值的欄位：{', '.join(self.missing_columns)}\n")
                else:
                    self.output_text.insert(tk.END, "資料中沒有缺失值。\n")

                # 類別型欄位
                self.categorical_columns = self.data.select_dtypes(include=['object']).columns.tolist()
                self.output_text.insert(tk.END, "\n=== 類別型欄位 ===\n")
                if self.categorical_columns:
                    self.output_text.insert(tk.END, f"類別型欄位：{', '.join(self.categorical_columns)}\n")
                else:
                    self.output_text.insert(tk.END, "無類別型欄位。\n")

                # 啟用解碼按鈕
                self.decode_button.configure(state='normal')
            except Exception as e:
                messagebox.showerror("錯誤", f"無法讀取檔案: {str(e)}")
                self.data = None
                self.missing_columns = None
                self.categorical_columns = None
        else:
            messagebox.showwarning("警告", "未選擇任何檔案")
    
    def decode_data(self):
        if self.data is not None:
            # 創建欄位刪除選項窗口
            self.create_delete_option_window()
        else:
            messagebox.showwarning("警告", "請先上傳資料")

    def create_delete_option_window(self):
        # 創建欄位刪除選項窗口
        delete_option_window = tk.Toplevel(self.root)
        delete_option_window.title("選擇欄位刪除方式")
        delete_option_window.geometry("400x250")
        delete_option_window.configure(bg='#E6E6FA')

        tk.Label(delete_option_window, text="選擇欄位刪除方式", font=('DFKai-SB', 16, 'bold'), bg='#E6E6FA').pack(anchor='center', padx=20, pady=10)

        # 自行處理按鈕
        tk.Button(
            delete_option_window,
            text="自行處理",
            command=lambda: [setattr(self, 'delete_columns', []), delete_option_window.destroy(), self.create_customization_window(True)],
            font=('DFKai-SB', 14),
            bg='#D8BFD8',
            fg='black'
        ).pack(anchor='center', expand=True, pady=10)

        # 預設處理按鈕
        tk.Button(
            delete_option_window,
            text="預設處理",
            command=lambda: [setattr(self, 'delete_columns', [col for col in ['RowNumber', 'Surname', 'CustomerId'] if col in self.data.columns]), delete_option_window.destroy(), self.create_customization_window(False)],
            font=('DFKai-SB', 14),
            bg='#D8BFD8',
            fg='black'
        ).pack(anchor='center', expand=True, pady=10)

        # 備註
        tk.Label(
            delete_option_window,
            text="預設處理將刪除 'RowNumber', 'Surname', 'CustomerId' 欄位",
            font=('DFKai-SB', 10),
            bg='#E6E6FA'
        ).pack(anchor='center', pady=5)

    def create_customization_window(self, allow_manual_delete):
        # 創建客製化選擇窗口
        custom_window = tk.Toplevel(self.root)
        custom_window.title("客製化數據處理選項")
        custom_window.geometry("600x600")
        custom_window.configure(bg='#E6E6FA')

        # 欄位刪除選項（僅在自行處理時顯示）
        if allow_manual_delete:
            tk.Label(custom_window, text="選擇要刪除的欄位", font=('DFKai-SB', 14, 'bold'), bg='#E6E6FA').pack(anchor='w', padx=20, pady=10)
            frame = tk.Frame(custom_window, bg='#E6E6FA')
            frame.pack(fill=tk.X, anchor='w', padx=10, pady=5)
            tk.Label(frame, text="刪除欄位數量：", font=('DFKai-SB', 12), bg='#E6E6FA').pack(side=tk.LEFT, padx=5)
            self.delete_count = tk.StringVar(value="0")
            ttk.Combobox(frame, textvariable=self.delete_count, values=[str(i) for i in range(len(self.data.columns) + 1)], state="readonly", font=('DFKai-SB', 12)).pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="選擇欄位", command=lambda: self.select_columns_to_delete(custom_window), font=('DFKai-SB', 12), bg='#D8BFD8', fg='black').pack(side=tk.LEFT, padx=10)

        # 缺失值處理選項
        tk.Label(custom_window, text="選擇缺失值處理方式", font=('DFKai-SB', 14, 'bold'), bg='#E6E6FA').pack(anchor='w', padx=20, pady=10)
        self.missing_value_choices = {}
        for col in self.missing_columns:
            frame = tk.Frame(custom_window, bg='#E6E6FA')
            frame.pack(fill=tk.X, anchor='w', padx=10, pady=5)
            tk.Label(frame, text=f"欄位 '{col}'（{'數值型' if self.data[col].dtype in ['int64', 'float64'] else '類別型'}）：", font=('DFKai-SB', 12), bg='#E6E6FA').pack(side=tk.LEFT, padx=5)
            choice = tk.StringVar(value="中位數" if self.data[col].dtype in ['int64', 'float64'] else "眾數")
            self.missing_value_choices[col] = choice
            ttk.Combobox(frame, textvariable=choice, values=["中位數", "眾數", "保留原本數值"], state="readonly", font=('DFKai-SB', 12)).pack(side=tk.LEFT, padx=5)
            tk.Label(frame, text="（建議：數值型用中位數，類別型用眾數，保留適用於分析缺失模式）", font=('DFKai-SB', 10), bg='#E6E6FA').pack(side=tk.LEFT, padx=5)

        # 類別特徵轉換選項
        tk.Label(custom_window, text="選擇類別特徵轉換方式", font=('DFKai-SB', 14, 'bold'), bg='#E6E6FA').pack(anchor='w', padx=20, pady=10)
        self.categorical_choices = {}
        for col in self.categorical_columns:
            frame = tk.Frame(custom_window, bg='#E6E6FA')
            frame.pack(fill=tk.X, anchor='w', padx=10, pady=5)
            tk.Label(frame, text=f"欄位 '{col}'（唯一值數：{self.data[col].nunique()}）：", font=('DFKai-SB', 12), bg='#E6E6FA').pack(side=tk.LEFT, padx=5)
            choice = tk.StringVar(value="Label Encoding" if self.data[col].nunique() <= 2 else "One-Hot Encoding")
            self.categorical_choices[col] = choice
            ttk.Combobox(frame, textvariable=choice, values=["Label Encoding", "One-Hot Encoding"], state="readonly", font=('DFKai-SB', 12)).pack(side=tk.LEFT, padx=5)
            tk.Label(frame, text="（建議：2個類別用 Label Encoding，多類別用 One-Hot Encoding）", font=('DFKai-SB', 10), bg='#E6E6FA').pack(side=tk.LEFT, padx=5)

        # 確認按鈕
        tk.Button(custom_window, text="確認並解碼", command=lambda: self.apply_custom_decoding(custom_window), font=('DFKai-SB', 12), bg='#D8BFD8', fg='black').pack(anchor='w', padx=20, pady=20)

    def select_columns_to_delete(self, parent_window):
        # 創建欄位選擇窗口
        delete_window = tk.Toplevel(parent_window)
        delete_window.title("選擇要刪除的欄位")
        delete_window.geometry("400x400")
        delete_window.configure(bg='#E6E6FA')

        count = int(self.delete_count.get())
        if count == 0:
            delete_window.destroy()
            return

        tk.Label(delete_window, text=f"請選擇 {count} 個欄位要刪除", font=('DFKai-SB', 14, 'bold'), bg='#E6E6FA').pack(anchor='w', padx=20, pady=10)
        self.delete_selections = []
        for _ in range(count):
            frame = tk.Frame(delete_window, bg='#E6E6FA')
            frame.pack(fill=tk.X, anchor='w', padx=10, pady=5)
            var = tk.StringVar()
            ttk.Combobox(frame, textvariable=var, values=list(self.data.columns), state="readonly", font=('DFKai-SB', 12)).pack(side=tk.LEFT, padx=5)
            self.delete_selections.append(var)

        tk.Button(delete_window, text="確認", command=lambda: [self.delete_columns.extend([var.get() for var in self.delete_selections if var.get()]), delete_window.destroy()], font=('DFKai-SB', 12), bg='#D8BFD8', fg='black').pack(anchor='w', padx=20, pady=20)
    
    def apply_custom_decoding(self, custom_window):
        try:
            # 清空文字和表格
            self.clear_table_frame()
            self.output_text.insert(tk.END, "=== 數據解碼處理 ===\n\n")

            # 1. 刪除選擇的欄位
            if self.delete_columns:
                unique_columns = list(dict.fromkeys(self.delete_columns))
                valid_columns = [col for col in unique_columns if col in self.data.columns]
                if valid_columns:
                    self.data = self.data.drop(valid_columns, axis=1)
                    self.output_text.insert(tk.END, f"已刪除欄位：{', '.join(valid_columns)}\n\n")
                    self.missing_columns = [col for col in self.missing_columns if col not in valid_columns]
                    self.categorical_columns = [col for col in self.categorical_columns if col not in valid_columns]

            # 2. 處理缺失值
            if self.missing_columns:
                self.output_text.insert(tk.END, "處理缺失值：\n")
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
                # 缺失值統計表格
                missing_values = self.data.isnull().sum()
                tree_missing = ttk.Treeview(self.inner_frame, columns=['欄位', '缺失值數量'], show='headings', height=len(missing_values))
                tree_missing.heading('欄位', text='欄位')
                tree_missing.heading('缺失值數量', text='缺失值數量')
                tree_missing.column('欄位', width=150, anchor='w')
                tree_missing.column('缺失值數量', width=100, anchor='w')
                for idx, (col, count) in enumerate(missing_values.items()):
                    tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
                    tree_missing.insert('', tk.END, values=[col, count], tags=tags)
                self.output_text.window_create(tk.END, window=tree_missing, padx=10, pady=5)
                self.output_text.insert(tk.END, "\n\n")
            else:
                self.output_text.insert(tk.END, "無缺失值需要處理。\n\n")

            # 3. 類別特徵轉換
            self.output_text.insert(tk.END, "=== 類別特徵轉換 ===\n")
            if self.categorical_columns:
                for col in self.categorical_columns[:]:
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
                    self.categorical_columns.remove(col)
                self.output_text.insert(tk.END, "\n")
            else:
                self.output_text.insert(tk.END, "無類別特徵需要轉換。\n\n")

            # 4. 顯示最終數據
            self.output_text.insert(tk.END, "=== 解碼後數據概述 ===\n")
            self.output_text.insert(tk.END, f"欄位名稱：{', '.join(self.data.columns)}\n")
            self.output_text.insert(tk.END, "前5行數據：\n\n")
            # 前5行數據表格
            tree = ttk.Treeview(self.inner_frame, columns=list(self.data.columns), show='headings', height=5)
            total_width = 0
            for col in self.data.columns:
                col_width = max(80, min(150, len(str(col)) * 8 + 50))
                tree.heading(col, text=col)
                tree.column(col, width=col_width, anchor='w')
                total_width += col_width
            if total_width > 1200:
                for col in self.data.columns:
                    tree.column(col, width=70)
            for idx, row in self.data.head().iterrows():
                tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
                tree.insert('', tk.END, values=[str(val) for val in row], tags=tags)
            self.output_text.window_create(tk.END, window=tree, padx=10, pady=5)
            self.output_text.insert(tk.END, "\n\n")

            self.output_text.insert(tk.END, "數據已準備好進行分析！\n")

            # 啟用分析和結果按鈕
            self.analysis_button.configure(state='normal')
            self.result_button.configure(state='normal')

            # 關閉客製化窗口
            custom_window.destroy()
        except Exception as e:
            messagebox.showerror("錯誤", f"數據解碼失敗: {str(e)}")

    def select_target_variable(self, algorithm_callback):
        # 創建目標變數選擇窗口
        target_window = tk.Toplevel(self.root)
        target_window.title("選擇目標變數")
        target_window.geometry("500x300")
        target_window.configure(bg='#E6E6FA')

        tk.Label(target_window, text="請選擇目標變數", font=self.font_chinese, bg='#E6E6FA').pack(pady=10)
        
        # 創建顯示列表，最後一欄添加「（預設）」
        columns_display = list(self.data.columns)
        default_column = self.data.columns[-1]
        columns_display[-1] = f"{default_column}（預設）"
        
        self.target_var = tk.StringVar(value=default_column)
        ttk.Combobox(target_window, textvariable=self.target_var, values=columns_display, state="readonly", font=self.font_english).pack(pady=10)
        tk.Label(target_window, text="（建議：選擇預測目標，如 'Exited' 或其他分類/回歸欄位）", font=self.font_chinese, bg='#E6E6FA').pack(pady=5)

        tk.Button(target_window, text="確認", command=lambda: self.set_target_and_run(algorithm_callback, target_window), font=self.font_chinese, bg='#D8BFD8').pack(pady=20)

    def set_target_and_run(self, algorithm_callback, target_window):
        # 儲存目標變數並執行
        selected_var = self.target_var.get()
        # 去除「（預設）」文字
        if selected_var.endswith("（預設）"):
            selected_var = selected_var[:-4]
        self.target_variable = selected_var
        target_window.destroy()
        
        if algorithm_callback.__name__ == 'run_all_algorithms_logic':
            self.run_all_algorithms_logic()
        else:
            self.select_split_ratio(algorithm_callback)

    def select_split_ratio(self, algorithm_callback):
        # 創建資料分割比例選擇窗口
        split_window = tk.Toplevel(self.root)
        split_window.title("選擇資料分割比例")
        split_window.geometry("500x300")
        split_window.configure(bg='#E6E6FA')

        tk.Label(split_window, text="請選擇訓練/測試資料分割比例", font=('DFKai-SB', 14, 'bold'), bg='#E6E6FA').pack(pady=10)
        self.split_ratio = tk.StringVar(value="8:2")
        ratios = ["9:1 (0.1)", "8:2 (0.2)", "7:3 (0.3)", "6:4 (0.4)", "5:5 (0.5)"]
        ttk.Combobox(split_window, textvariable=self.split_ratio, values=ratios, state="readonly", font=self.font_english).pack(pady=10)
        tk.Label(split_window, text="建議比例：\n- 決策樹：8:2\n- 隨機森林：9:1\n- SVM：7:3\n- SVM（調參）：7:3", font=self.font_chinese, bg='#E6E6FA').pack(pady=10)

        tk.Button(split_window, text="確認", command=lambda: [self.set_split_ratio_and_run(algorithm_callback, split_window)], font=self.font_chinese, bg='#D8BFD8').pack(pady=20)
    
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
        self.select_target_variable(self.run_decision_tree_logic)

    def run_decision_tree_logic(self):
        try:
            # 清空舊結果
            self.results.clear()
            self.current_algorithm = 'decision_tree'
            
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.clear_table_frame()  # 清空表格
            self.output_text.insert(tk.END, "=== 決策樹模型訓練 ===\n")
            self.output_text.insert(tk.END, f"目標變數: {self.target_variable}\n")
            self.output_text.insert(tk.END, f"使用演算法: 決策樹\n")

            # 定義特徵與標籤
            features = [col for col in self.data.columns if col != self.target_variable]
            X = self.data[features]
            y = self.data[self.target_variable]

            # 分割資料
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
            self.output_text.insert(tk.END, f"資料分割比例: 訓練 {int((1-self.test_size)*100)}% / 測試 {int(self.test_size*100)}%（建議：決策樹適用 8:2）\n")
            self.output_text.insert(tk.END, f"訓練資料筆數: {X_train.shape[0]}\n")
            self.output_text.insert(tk.END, f"測試資料筆數: {X_test.shape[0]}\n\n")

            # 決策樹初始化與訓練
            dt_classifier = DecisionTreeClassifier(max_depth=5, random_state=42)
            self.output_text.insert(tk.END, "決策樹模型參數：\n")
            self.output_text.insert(tk.END, f"{dt_classifier.get_params()}\n\n")
            dt_classifier.fit(X_train, y_train)

            # 模型預測
            y_pred = dt_classifier.predict(X_test)

            # 儲存結果
            self.results['decision_tree'] = {
                'model': dt_classifier,
                'features': features,
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'y_pred': y_pred,
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='binary'),
                'recall': recall_score(y_test, y_pred, average='binary'),
                'f1': f1_score(y_test, y_pred, average='binary'),
                'classification_report': classification_report(y_test, y_pred)
            }

            self.output_text.insert(tk.END, "決策樹模型訓練完畢！請按「分析結果」查看評估指標與圖表。\n")
            self.result_button.config(state='normal')  # 啟用分析結果按鈕
        except Exception as e:
            messagebox.showerror("錯誤", f"決策樹訓練失敗: {str(e)}")

    def run_random_forest(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.select_target_variable(self.run_random_forest_logic)

    def run_random_forest_logic(self):
        try:
            # 清空舊結果
            self.results.clear()
            self.current_algorithm = 'random_forest'
            
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.clear_table_frame()  # 清空表格
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

            # 儲存結果
            self.results['random_forest'] = {
                'model': rf_classifier,
                'features': features,
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'y_pred': y_pred,
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='binary'),
                'recall': recall_score(y_test, y_pred, average='binary'),
                'f1': f1_score(y_test, y_pred, average='binary'),
                'classification_report': classification_report(y_test, y_pred)
            }

            self.output_text.insert(tk.END, "隨機森林模型訓練完畢！請按「分析結果」查看評估指標與圖表。\n")
            self.result_button.config(state='normal')  # 啟用分析結果按鈕
        except Exception as e:
            messagebox.showerror("錯誤", f"隨機森林訓練失敗: {str(e)}")

    def run_svm(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.select_target_variable(self.run_svm_logic)

    def run_svm_logic(self):
        try:
            # 清空舊結果
            self.results.clear()
            self.current_algorithm = 'svm'
            
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.clear_table_frame()  # 清空表格
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

            # 儲存結果
            self.results['svm'] = {
                'model': svm_model,
                'features': features,
                'X_train': X_train,
                'X_train_scaled': X_train_scaled,
                'X_test_scaled': X_test_scaled,
                'y_train': y_train,
                'y_test': y_test,
                'y_pred': y_pred,
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='binary'),
                'recall': recall_score(y_test, y_pred, average='binary'),
                'f1': f1_score(y_test, y_pred, average='binary'),
                'classification_report': classification_report(y_test, y_pred)
            }

            self.output_text.insert(tk.END, "SVM 模型訓練完畢！請按「分析結果」查看評估指標與圖表。\n")
            self.result_button.config(state='normal')  # 啟用分析結果按鈕
        except Exception as e:
            messagebox.showerror("錯誤", f"SVM 訓練失敗: {str(e)}")

    def run_svm_tuned(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.select_target_variable(self.run_svm_tuned_logic)

    def run_svm_tuned_logic(self):
        try:
            # 清空舊結果
            self.results.clear()
            self.current_algorithm = 'svm_tuned'
            
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.clear_table_frame()  # 清空表格
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

            # 儲存結果
            self.results['svm_tuned'] = {
                'model': svm_model,
                'features': features,
                'X_train': X_train,
                'X_train_scaled': X_train_scaled,
                'X_test_scaled': X_test_scaled,
                'y_train': y_train,
                'y_test': y_test,
                'y_pred': y_pred,
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='binary'),
                'recall': recall_score(y_test, y_pred, average='binary'),
                'f1': f1_score(y_test, y_pred, average='binary'),
                'classification_report': classification_report(y_test, y_pred)
            }

            self.output_text.insert(tk.END, "SVM（調參）模型訓練完畢！請按「分析結果」查看評估指標與圖表。\n")
            self.result_button.config(state='normal')  # 啟用分析結果按鈕
        except Exception as e:
            messagebox.showerror("錯誤", f"SVM（調參）訓練失敗: {str(e)}")

    def run_all_algorithms(self):
        if self.data is None:
            messagebox.showwarning("警告", "請先上傳並解碼資料")
            return
        self.select_target_variable(self.run_all_algorithms_logic)

    def run_all_algorithms_logic(self):
        try:
            # 清空舊結果
            self.results.clear()
            self.current_algorithm = 'all_algorithms'
            
            # 清空輸出區域
            self.output_text.delete(1.0, tk.END)
            self.clear_table_frame()
            self.output_text.insert(tk.END, "=== 所有演算法模型訓練 ===\n")
            self.output_text.insert(tk.END, f"目標變數: {self.target_variable}\n")

            # 定義特徵與標籤
            features = [col for col in self.data.columns if col != self.target_variable]
            X = self.data[features]
            y = self.data[self.target_variable]

            algorithms = [
                ('decision_tree', 0.2, DecisionTreeClassifier(max_depth=5, random_state=42), '決策樹', 8),
                ('random_forest', 0.1, RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42), '隨機森林', 9),
                ('svm', 0.3, SVC(kernel='rbf', random_state=42), 'SVM', 7),
                ('svm_tuned', 0.3, SVC(kernel='rbf', C=1, gamma=0.1, random_state=42), 'SVM（調參）', 7)
            ]

            for algo_name, test_size, model, algo_display, train_ratio in algorithms:
                self.output_text.insert(tk.END, f"\n=== 訓練 {algo_display} ===\n")
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
                self.output_text.insert(tk.END, f"資料分割比例: 訓練 {train_ratio}0% / 測試 {10-train_ratio}0%（{algo_display}推薦比例）\n")
                self.output_text.insert(tk.END, f"訓練資料筆數: {X_train.shape[0]}\n")
                self.output_text.insert(tk.END, f"測試資料筆數: {X_test.shape[0]}\n\n")

                if algo_name in ['svm', 'svm_tuned']:
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                else:
                    X_train_scaled, X_test_scaled = X_train, X_test

                self.output_text.insert(tk.END, f"{algo_display}模型參數：\n")
                self.output_text.insert(tk.END, f"{model.get_params()}\n\n")
                model.fit(X_train_scaled, y_train)

                y_pred = model.predict(X_test_scaled)

                self.results[algo_name] = {
                    'model': model,
                    'features': features,
                    'X_train': X_train,
                    'X_test': X_test,
                    'X_train_scaled': X_train_scaled if algo_name in ['svm', 'svm_tuned'] else None,
                    'X_test_scaled': X_test_scaled if algo_name in ['svm', 'svm_tuned'] else None,
                    'y_train': y_train,
                    'y_test': y_test,
                    'y_pred': y_pred,
                    'confusion_matrix': confusion_matrix(y_test, y_pred),
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, average='binary'),
                    'recall': recall_score(y_test, y_pred, average='binary'),
                    'f1': f1_score(y_test, y_pred, average='binary'),
                    'classification_report': classification_report(y_test, y_pred)
                }

                self.output_text.insert(tk.END, f"{algo_display}模型訓練完畢！\n")

            self.output_text.insert(tk.END, "\n所有演算法訓練完畢！請按「分析結果」查看比較表格與圖表。\n")
            self.result_button.config(state='normal')
        except Exception as e:
            messagebox.showerror("錯誤", f"所有演算法訓練失敗: {str(e)}")

    def show_results(self):
        if not self.results or self.current_algorithm not in self.results and self.current_algorithm != 'all_algorithms':
            messagebox.showwarning("警告", "尚未執行任何演算法訓練，請先執行「數據分析」")
            return
        # 清空輸出區域
        self.clear_table_frame()
        self.output_text.insert(tk.END, "=== 客戶流失預測結果 ===\n\n")

        # 選擇顯示的演算法（單一演算法或最後一個）
        display_algo = self.current_algorithm if self.current_algorithm != 'all_algorithms' else 'svm_tuned'
        result = self.results[display_algo]
        algo_name = {
            'decision_tree': '決策樹',
            'random_forest': '隨機森林',
            'svm': 'SVM (未調參)',
            'svm_tuned': 'SVM (調參, C=1, gamma=0.1)'
        }[display_algo]
        algo_name_en = {
            'decision_tree': 'Decision Tree',
            'random_forest': 'Random Forest',
            'svm': 'SVM',
            'svm_tuned': 'SVM Tuned'
        }[display_algo]

        # 計算流失客戶數量與比例
        y_pred = result['y_pred']
        X_test = result['X_test']
        churn_count = sum(y_pred == 1)
        churn_rate = churn_count / len(y_pred) * 100
        total_customers = len(y_pred)
        
        # 設定表格樣式
        style = ttk.Style()
        style.configure('Team.Treeview', font=('DFKai-SB', 16), rowheight=30)
        style.configure('Team.Treeview.Heading', font=('DFKai-SB', 16))

        # 流失概況表格
        self.output_text.insert(tk.END, "流失概況：\n\n")
        columns = ["項目", "值"]
        tree_summary = ttk.Treeview(self.inner_frame, columns=columns, show='headings', height=2, style='Team.Treeview')
        tree_summary.heading("項目", text="項目")
        tree_summary.heading("值", text="值")
        tree_summary.column("項目", width=150, anchor='w')
        tree_summary.column("值", width=100, anchor='w')
        tree_summary.insert('', tk.END, values=["流失客戶數", f"{churn_count}"], tags='oddrow')
        tree_summary.insert('', tk.END, values=["流失比例", f"{churn_rate:.1f}%"], tags='evenrow')
        self.output_text.window_create(tk.END, window=tree_summary, padx=10, pady=5)
        self.output_text.insert(tk.END, "\n\n")

        # 直觀文字解釋
        self.output_text.insert(tk.END, f"根據 {algo_name} 的預測結果：\n")
        self.output_text.insert(tk.END, f"- 在 {total_customers} 名測試客戶中，預計 {churn_count} 名客戶可能流失，流失比例為 {churn_rate:.1f}%。\n")

        # 高風險客戶特徵分析
        if churn_count > 0:
            churn_data = X_test[y_pred == 1]
            key_features = ['Age', 'Balance', 'Geography'] if 'Geography' in X_test.columns else ['Age', 'Balance']
            feature_summary = []
            for feature in key_features:
                if feature == 'Age':
                    mean_age = churn_data[feature].mean()
                    feature_summary.append(f"平均年齡：{mean_age:.1f} 歲")
                elif feature == 'Balance':
                    mean_balance = churn_data[feature].mean()
                    feature_summary.append(f"平均餘額：${mean_balance:.2f}")
                elif feature == 'Geography':
                    top_geo = churn_data[feature].mode()[0]
                    feature_summary.append(f"主要地區：{top_geo}")
            self.output_text.insert(tk.END, f"- 流失風險高的客戶特徵：\n  - {'；'.join(feature_summary)}。\n")
        else:
            self.output_text.insert(tk.END, "- 無客戶預測為流失，表現優異！\n")

        # 針對性建議
        self.output_text.insert(tk.END, "\n建議：\n")
        if churn_rate > 20:
            self.output_text.insert(tk.END, "- 流失比例較高，建議針對高風險客戶（如高餘額或中高齡客戶）推出專屬優惠或忠誠計畫。\n")
        elif churn_rate > 5:
            self.output_text.insert(tk.END, "- 流失比例適中，建議加強客戶關係管理，特別關注高餘額客戶。\n")
        else:
            self.output_text.insert(tk.END, "- 流失比例低，持續保持優質服務，並定期監控客戶滿意度！\n")



        # 技術指標表格
        self.output_text.insert(tk.END, "\n=== 技術評估指標 ===\n\n")
        if self.current_algorithm == 'all_algorithms':
            self.output_text.insert(tk.END, "所有演算法性能比較：\n\n")
            columns = ["指標", "決策樹", "隨機森林", "SVM", "SVM (調參)"]
            tree_compare = ttk.Treeview(self.inner_frame, columns=columns, show='headings', height=4,style='Team.Treeview')
            tree_compare.heading("指標", text="指標")
            tree_compare.heading("決策樹", text="決策樹")
            tree_compare.heading("隨機森林", text="隨機森林")
            tree_compare.heading("SVM", text="SVM")
            tree_compare.heading("SVM (調參)", text="SVM (調參)")
            tree_compare.column("指標", width=100, anchor='w')
            tree_compare.column("決策樹", width=100, anchor='w')
            tree_compare.column("隨機森林", width=100, anchor='w')
            tree_compare.column("SVM", width=100, anchor='w')
            tree_compare.column("SVM (調參)", width=100, anchor='w')
            metrics = ["準確率", "精確率", "召回率", "F1 分數"]
            metric_keys = ["accuracy", "precision", "recall", "f1"]
            for idx, (metric, key) in enumerate(zip(metrics, metric_keys)):
                tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
                values = [metric]
                for algo in ['decision_tree', 'random_forest', 'svm', 'svm_tuned']:
                    values.append(f"{self.results[algo][key]:.4f}")
                tree_compare.insert('', tk.END, values=values, tags=tags)
            self.output_text.window_create(tk.END, window=tree_compare, padx=10, pady=5)
            self.output_text.insert(tk.END, "\n\n")
        
        self.output_text.insert(tk.END, f"{algo_name} 模型性能表格：\n\n")
        columns = ["指標", algo_name]
        tree_metrics = ttk.Treeview(self.inner_frame, columns=columns, show='headings', height=4,style='Team.Treeview')
        tree_metrics.heading("指標", text="指標")
        tree_metrics.heading(algo_name, text=algo_name)
        tree_metrics.column("指標", width=100, anchor='w')
        tree_metrics.column(algo_name, width=100, anchor='w')
        metrics = ["準確率", "精確率", "召回率", "F1 分數"]
        metric_keys = ["accuracy", "precision", "recall", "f1"]
        for idx, (metric, key) in enumerate(zip(metrics, metric_keys)):
            tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
            tree_metrics.insert('', tk.END, values=[metric, f"{result[key]:.4f}"], tags=tags)
        self.output_text.window_create(tk.END, window=tree_metrics, padx=10, pady=5)
        self.output_text.insert(tk.END, "\n\n")

        # 銷毀舊圖表窗口
        if self.graph_window is not None:
            self.graph_window.destroy()

        # 創建新圖表窗口
        self.graph_window = tk.Toplevel(self.root)
        self.graph_window.title(f"{algo_name_en} Visualization Results")
        self.graph_window.geometry("1200x600")
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
        axes = [axes]

        # 混淆矩陣
        sns.heatmap(result['confusion_matrix'], annot=True, fmt="d", cmap="Blues", ax=axes[0][0])
        axes[0][0].set_xlabel("Predicted Label")
        axes[0][0].set_ylabel("True Label")
        axes[0][0].set_title(f"{algo_name_en} Confusion Matrix")

        # 演算法特定視覺化
        if display_algo == 'decision_tree':
            plot_tree(result['model'], feature_names=result['features'], class_names=['Not Churned', 'Churned'], filled=True, rounded=True, ax=axes[0][1])
            axes[0][1].set_title(f"{algo_name_en} (max_depth=5)")
        elif display_algo == 'random_forest':
            plot_tree(result['model'].estimators_[0], feature_names=result['features'], class_names=['Not Churned', 'Churned'], filled=True, rounded=True, ax=axes[0][1])
            axes[0][1].set_title(f"{algo_name_en} First Tree (max_depth=5)")
        elif display_algo in ['svm', 'svm_tuned']:
            pca = PCA(n_components=2)
            X_train_pca = pca.fit_transform(result['X_train_scaled'] if 'X_train_scaled' in result else result['X_train'])
            svm_pca = SVC(kernel='rbf', probability=True, random_state=42, C=1, gamma=0.1 if display_algo == 'svm_tuned' else 1.0)
            svm_pca.fit(X_train_pca, result['y_train'])
            x_min, x_max = X_train_pca[:, 0].min() - 1, X_train_pca[:, 0].max() + 1
            y_min, y_max = X_train_pca[:, 1].min() - 1, X_train_pca[:, 1].max() + 1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))
            Z = svm_pca.predict(np.array([xx.ravel(), yy.ravel()]).T)
            Z = Z.reshape(xx.shape)
            axes[0][1].contourf(xx, yy, Z, alpha=0.75, cmap=ListedColormap(('red', 'green')))
            axes[0][1].scatter(X_train_pca[:, 0], X_train_pca[:, 1], c=result['y_train'], edgecolors='k', cmap=ListedColormap(('red', 'green')))
            axes[0][1].set_title(f"{algo_name_en} Decision Boundary (PCA-Reduced Space)")
            axes[0][1].set_xlabel("Principal Component 1")
            axes[0][1].set_ylabel("Principal Component 2")

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.output_text.insert(tk.END, f"已顯示 {algo_name} 的客戶流失預測結果與技術報告！\n")

    def show_system_intro(self):
        # 清空輸出區域
        self.clear_table_frame()
        self.output_text.insert(tk.END, "=== 系統介紹 ===\n\n")
        intro_text = """本研究旨在透過多種監督式學習模型（例如：決策樹、隨機森林與支持向量機），預測銀行客戶可能流失的風險。客戶流失一直是金融業的一大挑戰，流失的客戶不僅會直接影響銀行的收入，還可能損害銀行的品牌形象與市場地位。因此，如何提前預測哪些客戶可能流失並採取有效的挽留措施，是銀行提升客戶關係管理及市場競爭力的重要方向。

    銀行客戶流失的主要原因，可能包括服務體驗不佳、競爭對手的吸引、更高的手續費或利率，以及個人財務狀況的變化等。本專案通過分析多種客戶特徵（如信用評分、年齡、地理位置和產品使用數量等），建構預測模型，協助銀行識別高風險客戶群體，並提供數據支持以制定精準的留客策略。

    我們希望透過本研究，能夠：
    - 提升對客戶資料的洞察力，了解哪些因素最能影響客戶流失。
    - 選擇最佳的機器學習模型，用於準確預測客戶流失的可能性。
    - 為銀行提供可操作的建議，幫助其制定針對性的行銷策略與服務改善方案。

    此外，我們也針對模型的準確性、穩定性及應用場景進行詳細比較，力求提供一套兼具實用性與效能的解決方案。"""
        self.output_text.insert(tk.END, intro_text + "\n")

    def show_team_info(self):
            # 清空輸出區域
            self.clear_table_frame()
            self.output_text.insert(tk.END, "=== 製作團隊 ===\n\n")

            # 定義團隊資料
            team_data = [
                {"name": "B1011035 高鈿傑", "tasks": "專案介紹、數據描述"},
                {"name": "B1112204 何虹儀", "tasks": "模型選擇與訓練、預測結果、簡報製作與優化"},
                {"name": "B1141065 陳昱安", "tasks": "主要程式撰寫、系統建立與製作、書面報告格式之排版"}
            ]
            # 配置表格樣式
            style = ttk.Style()
            style.configure('Team.Treeview', font=('DFKai-SB', 16), rowheight=30)
            style.configure('Team.Treeview.Heading', font=('DFKai-SB', 16))

            # 創建表格
            self.output_text.insert(tk.END, "團隊成員與工作項目：\n\n")
            columns = ["姓名", "工作項目"]
            tree = ttk.Treeview(self.inner_frame, columns=columns, show='headings', height=3, style='Team.Treeview')
            tree.heading("姓名", text="姓名")
            tree.heading("工作項目", text="工作項目")
            tree.column("姓名", width=200, anchor='w')
            tree.column("工作項目", width=550, anchor='w')
            for idx, member in enumerate(team_data):
                tags = 'oddrow' if idx % 2 == 0 else 'evenrow'
                tree.insert('', tk.END, values=[member["name"], member["tasks"]], tags=tags)
            self.output_text.window_create(tk.END, window=tree, padx=10, pady=5)
            self.output_text.insert(tk.END, "\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankChurnApp(root)
    root.mainloop()