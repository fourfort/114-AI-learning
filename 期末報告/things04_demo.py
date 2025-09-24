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