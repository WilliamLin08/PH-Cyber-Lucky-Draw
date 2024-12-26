import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import csv
import os
from datetime import datetime

class LotteryScratchCard20:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("刮刮乐 - 20元圣诞奖池")
        self.root.geometry("600x850")

        # 设置圣诞主题背景
        self.root.configure(bg='#e8f5e9')

        # ===================== 核心逻辑变量 =====================

        # 奖项及概率（示例，可根据需求调整）
        self.prizes = {
            "🎁 特等奖 (500元)": 0.002,
            "🎄 一等奖 (200元)": 0.01,
            "🎅 二等奖 (50元)": 0.05,
            "❄️ 三等奖 (30元)": 0.10,
            "☃️ 四等奖 (可乐2元)": 0.25,
            "🎉 再来一次": 0.15,
            "🔔 未中奖": 0.438
        }

        # 刮开区域追踪
        self.scratch_matrix = None
        self.revealed = False
        self.canvas_width = 500
        self.canvas_height = 300
        self.matrix_scale = 1  # 用于鼠标刮开时的矩阵追踪

        # 财务与抽奖次数
        self.total_income = 0  # 总收入
        self.total_payout = 0  # 总支出（不包含“可乐2元”）
        self.net_income = 0    # 净收入
        self.count = 0         # 游戏总次数

        # 抽奖次数
        self.allowed_plays = 0  # 可玩次数，手动设置

        # “再来一次”免费资格
        self.is_free_game = False

        # 奖项统计：记录本轮设置次数内，各奖项的抽中次数
        self.prize_counts = {
            "🎁 特等奖 (500元)": 0,
            "🎄 一等奖 (200元)": 0,
            "🎅 二等奖 (50元)": 0,
            "❄️ 三等奖 (30元)": 0,
            "☃️ 可乐/零食": 0,
            "🎉 再来一次": 0,
            "🔔 未中奖": 0
        }

        # CSV 文件记录
        self.csv_file = "lottery_results_20yuan.csv"
        self.initialize_csv()

        # 创建界面元素
        self.create_widgets()

        # 绑定按键
        self.root.bind('<space>', lambda event: self.start_new_game(charge=True))
        self.root.bind('<r>', lambda event: self.reveal_all())

    def initialize_csv(self):
        """若 CSV 不存在则创建，并写入表头"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Prize", "Income (元)", "Payout (元)", "Net Income (元)"])

    def create_widgets(self):
        """
        创建 Tkinter 界面布局
        """
        # ==================== 圣诞祝福语 ====================
        christmas_label = tk.Label(self.root,
                                   text="🎄❄️ 圣诞快乐！❄️🎄\n🎅🎁 祝您好运！🎁🎅",
                                   font=("Brush Script MT", 24, "italic"),
                                   fg='#c62828',  # 深红色文字
                                   bg='#e8f5e9')
        christmas_label.pack(pady=15)

        # ===================== 标题 =====================
        title_label = tk.Label(self.root, text="刮刮乐 - 20元圣诞奖池",
                               font=("Arial", 24, "bold"),
                               fg='#1b5e20',  # 深绿色
                               bg='#e8f5e9')
        title_label.pack(pady=10)

        # ===================== 按钮框架 =====================
        button_frame = tk.Frame(self.root, bg='#e8f5e9')
        button_frame.pack(pady=10)

        # “开始新游戏”按钮
        self.start_button = tk.Button(button_frame,
                                      text="开始新游戏 (空格)",
                                      command=lambda: self.start_new_game(charge=True),
                                      font=("Arial", 14, "bold"),
                                      bg='#43a047',  # 绿色按钮
                                      fg='black',
                                      relief=tk.FLAT,
                                      padx=15,
                                      pady=5,
                                      cursor="hand2")
        self.start_button.pack(side=tk.LEFT, padx=15)

        # “一键刮开”按钮
        self.reveal_button = tk.Button(button_frame,
                                       text="一键刮开 (按 R)",
                                       command=self.reveal_all,
                                       state=tk.DISABLED,
                                       font=("Arial", 14, "bold"),
                                       bg='#43a047',
                                       fg='black',
                                       relief=tk.FLAT,
                                       padx=15,
                                       pady=5,
                                       cursor="hand2")
        self.reveal_button.pack(side=tk.LEFT, padx=15)

        # “设置抽奖次数”按钮
        self.setup_plays_button = tk.Button(button_frame,
                                            text="设置抽奖次数",
                                            command=self.show_set_plays_dialog,
                                            font=("Arial", 14, "bold"),
                                            bg='#fdd835',  # 金黄色
                                            fg='black',
                                            relief=tk.FLAT,
                                            padx=15,
                                            pady=5,
                                            cursor="hand2")
        self.setup_plays_button.pack(side=tk.LEFT, padx=15)

        # ===================== 画布框架 =====================
        self.frame = tk.Frame(self.root, bg='#e8f5e9')
        self.frame.pack(pady=20)

        # 创建画布
        self.canvas = tk.Canvas(self.frame,
                                width=self.canvas_width,
                                height=self.canvas_height,
                                bg='white',
                                relief=tk.FLAT,
                                bd=0,
                                cursor="crosshair")
        self.canvas.pack()

        # 初始状态隐藏画布框架
        self.frame.pack_forget()

        # ===================== 信息区域 =====================
        info_frame = tk.Frame(self.root, bg='#e8f5e9')
        info_frame.pack(pady=10)

        # 显示游戏总次数
        self.game_count_label = tk.Label(info_frame,
                                         text="游戏总次数: 0",
                                         font=("Arial", 14),
                                         bg='#e8f5e9',
                                         fg='#0277bd')
        self.game_count_label.pack(side=tk.LEFT, padx=10)

        # 显示剩余可玩次数
        self.remaining_plays_label = tk.Label(self.root,
                                              text="剩余可玩次数: 未设置",
                                              font=("Arial", 14),
                                              bg='#e8f5e9',
                                              fg='#0277bd')
        self.remaining_plays_label.pack(pady=10)

        # ===================== 管理员入口 =====================
        self.admin_button = tk.Button(self.root,
                                      text="管理员入口",
                                      command=self.show_admin_login_dialog,
                                      font=("Arial", 12, "bold"),
                                      bg='#f9a825',  # 金黄色
                                      fg='black',
                                      relief=tk.FLAT,
                                      padx=10,
                                      pady=5,
                                      cursor="hand2")
        self.admin_button.place(x=500, y=10)

        # ===================== 按钮悬停效果 =====================
        self.setup_button_hover()

        # ===================== 初始化按钮状态 =====================
        self.update_start_button_state()

    def setup_button_hover(self):
        """设置按钮悬停颜色"""
        def on_enter(e):
            btn = e.widget
            if btn == self.admin_button:
                e.widget['background'] = '#ffeb3b'  # 更亮的黄色
            elif btn == self.setup_plays_button:
                e.widget['background'] = '#ffd54f'  # 更亮的金黄色
            else:
                e.widget['background'] = '#66bb6a'  # 更亮的绿色

        def on_leave(e):
            btn = e.widget
            if btn == self.admin_button:
                e.widget['background'] = '#f9a825'  # 原黄色
            elif btn == self.setup_plays_button:
                e.widget['background'] = '#fdd835'  # 原金黄色
            elif btn == self.reveal_button or btn == self.start_button:
                e.widget['background'] = '#43a047'  # 原绿色

        for b in [self.start_button, self.reveal_button, self.setup_plays_button, self.admin_button]:
            b.bind("<Enter>", on_enter)
            b.bind("<Leave>", on_leave)

    # --------------------- 抽奖次数相关 ---------------------
    def update_start_button_state(self):
        """根据 self.allowed_plays 是否大于 0，决定是否启用“开始新游戏”"""
        if self.allowed_plays > 0:
            self.start_button.config(state=tk.NORMAL)
            self.remaining_plays_label.config(text=f"剩余可玩次数: {self.allowed_plays}")
        else:
            self.start_button.config(state=tk.DISABLED)
            if self.allowed_plays == 0:
                self.remaining_plays_label.config(text="剩余可玩次数: 0")

    def show_set_plays_dialog(self):
        """弹窗设置抽奖次数，并清空本次 session 的奖项统计"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置抽奖次数")
        dialog.geometry("300x200")
        dialog.config(bg="#fff8e1")

        label = tk.Label(dialog, text="请输入抽奖次数：", bg="#fff8e1", font=("Arial", 12))
        label.pack(pady=20)

        entry = tk.Entry(dialog, font=("Arial", 14))
        entry.pack(pady=10)

        confirm_button = tk.Button(dialog,
                                   text="确定",
                                   command=lambda: self.confirm_plays(dialog, entry),
                                   font=("Arial", 12, "bold"),
                                   bg='#43a047',
                                   fg='black',
                                   relief=tk.FLAT,
                                   padx=10,
                                   pady=5,
                                   cursor="hand2")
        confirm_button.pack(pady=10)

    def confirm_plays(self, dialog, entry):
        """确认输入的抽奖次数"""
        val = entry.get()
        try:
            val = int(val)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
            return

        if val <= 0:
            messagebox.showerror("错误", "抽奖次数必须为正数！")
        else:
            self.allowed_plays = val
            dialog.destroy()

            # 清空当前 session 的奖项统计
            for k in self.prize_counts:
                self.prize_counts[k] = 0

            self.update_start_button_state()

    # --------------------- 开始新游戏 ---------------------
    def start_new_game(self, charge=True):
        """
        当点击开始游戏时，如果 allowed_plays > 0，才可以真正开始。
        若拥有再来一次资格，则不扣减次数。
        """
        # 如果有再来一次资格，则本次不收费
        if self.is_free_game:
            charge = False
            self.is_free_game = False

        if self.allowed_plays <= 0 and charge:
            messagebox.showwarning("提醒", "当前抽奖次数已用完，请重新设置抽奖次数。")
            return

        # 若按钮已禁用，直接返回
        if str(self.start_button['state']) == 'disabled':
            return

        # 临时禁用按钮防止重复点击
        self.start_button.config(state=tk.DISABLED)

        if charge:
            # 扣费 20 元
            self.total_income += 20
            self.allowed_plays -= 1
            self.update_start_button_state()

        # 重置刮开区域追踪
        self.scratch_matrix = np.zeros((self.canvas_height // self.matrix_scale,
                                        self.canvas_width // self.matrix_scale))
        self.revealed = False

        # 显示画布框架
        self.frame.pack(pady=10)
        self.canvas.delete("all")

        # 启用“一键刮开”
        self.reveal_button.config(state=tk.NORMAL)

        # 决定中奖结果
        self.current_prize = self.determine_prize()

        # 绘制中奖文字
        self.canvas.create_text(self.canvas_width // 2,
                                self.canvas_height // 2,
                                text=self.current_prize,
                                font=("Arial", 36, "bold"),
                                fill="#d32f2f" if "奖" in self.current_prize else "#455a64",
                                tags="prize")

        # 创建灰色覆盖层
        self.create_scratch_layer()

        # 绑定鼠标事件
        self.canvas.bind("<B1-Motion>", self.scratch)
        self.canvas.bind("<Button-1>", self.scratch)

        # 若次数用完，弹窗显示本次 session 的统计
        if self.allowed_plays == 0 and not self.is_free_game:
            self.show_session_summary_popup()

        # 稍等后再恢复按钮
        self.root.after(500, lambda: self.update_start_button_state())

    # --------------------- 刮开操作 ---------------------
    def reveal_all(self, *_):
        """一键刮开"""
        if str(self.reveal_button['state']) == 'disabled':
            return

        # 删掉“scratch”标签覆盖层
        self.canvas.delete("scratch")
        self.revealed = True
        self.reveal_button.config(state=tk.DISABLED)

    def create_scratch_layer(self):
        """使用小矩形覆盖画布，实现刮开效果"""
        rect_size = 12
        for x in range(0, self.canvas_width, rect_size):
            for y in range(0, self.canvas_height, rect_size):
                self.canvas.create_rectangle(x, y, x + rect_size, y + rect_size,
                                             fill='#9e9e9e',
                                             outline='#9e9e9e',
                                             tags="scratch")

    def scratch(self, event):
        """鼠标刮开"""
        x, y = event.x, event.y
        r = 25
        overlapping = self.canvas.find_overlapping(x - r, y - r, x + r, y + r)
        for item in overlapping:
            if "scratch" in self.canvas.gettags(item):
                self.canvas.delete(item)

        # 更新刮开矩阵
        matrix_x = min(y // self.matrix_scale, self.scratch_matrix.shape[0] - 1)
        matrix_y = min(x // self.matrix_scale, self.scratch_matrix.shape[1] - 1)

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                new_x = matrix_x + dx
                new_y = matrix_y + dy
                if (0 <= new_x < self.scratch_matrix.shape[0]
                        and 0 <= new_y < self.scratch_matrix.shape[1]):
                    self.scratch_matrix[new_x, new_y] = 1

        # 如果刮开面积超过 30%，禁用“一键刮开”按钮
        scratched_percentage = np.sum(self.scratch_matrix) / self.scratch_matrix.size
        if scratched_percentage > 0.3 and not self.revealed:
            self.revealed = True
            self.reveal_button.config(state=tk.DISABLED)

    # --------------------- 中奖逻辑 ---------------------
    def determine_prize(self):
        """
        随机抽取奖项，无保底
        """
        rand_num = random.random()
        cumulative_prob = 0
        for prize, prob in self.prizes.items():
            cumulative_prob += prob
            if rand_num <= cumulative_prob:
                # 如果奖项是“再来一次”，设置免费游戏
                if prize == "🎉 再来一次":
                    self.is_free_game = True
                # 记录中奖
                self.update_payout(prize)
                self.log_result(prize)
                self.update_game_count()
                return prize
        return "🔔 未中奖"

    def update_payout(self, prize):
        """
        根据奖项更新总支出：四等奖(可乐2元)不计入支出，其余按照金额统计
        """
        if "四等奖" in prize or "再来一次" in prize or "未中奖" in prize:
            payout = 0
        else:
            # 根据奖项名称提取金额
            if "500元" in prize:
                payout = 500
            elif "200元" in prize:
                payout = 200
            elif "50元" in prize:
                payout = 50
            elif "30元" in prize:
                payout = 30
            else:
                payout = 0

        self.total_payout += payout
        self.update_financial_metrics()

    def update_financial_metrics(self):
        """更新净收入"""
        self.net_income = self.total_income - self.total_payout

    def log_result(self, prize):
        """记录到 CSV，并更新当前 session 的奖项统计"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 计算写入 CSV 的 payout
        if "四等奖" in prize or "再来一次" in prize or "未中奖" in prize:
            payout_record = 0
        elif "500元" in prize:
            payout_record = 500
        elif "200元" in prize:
            payout_record = 200
        elif "50元" in prize:
            payout_record = 50
        elif "30元" in prize:
            payout_record = 30
        else:
            payout_record = 0

        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                prize,
                self.total_income,
                payout_record,
                self.net_income
            ])

        # 更新 session 统计
        if prize in self.prize_counts:
            self.prize_counts[prize] += 1

    def update_game_count(self):
        """游戏次数 +1，并更新界面"""
        self.count += 1
        self.game_count_label.config(text=f"游戏总次数: {self.count}")

    # --------------------- 次数结束后弹窗统计 ---------------------
    def show_session_summary_popup(self):
        """
        当抽奖次数用完后，弹窗显示本 session 各奖项情况，然后重置。
        """
        popup = tk.Toplevel(self.root)
        popup.title("本次抽奖总结")
        popup.geometry("350x450")
        popup.config(bg="#fafafa")

        # 圣诞装饰
        decoration_label = tk.Label(popup,
                                    text="🎄🎉 本次抽奖统计结果 🎉🎄",
                                    font=("Arial", 16, "bold"),
                                    bg="#fafafa",
                                    fg='#d32f2f')
        decoration_label.pack(pady=10)

        # 构造统计字符串
        summary_text = ""
        for k, v in self.prize_counts.items():
            summary_text += f"{k}: {v}\n"

        text_label = tk.Label(popup,
                              text=summary_text.strip(),
                              font=("Arial", 12),
                              bg="#fafafa",
                              justify=tk.LEFT)
        text_label.pack(pady=10)

        # 添加圣诞图片或符号（例如雪花）
        snow_label = tk.Label(popup,
                              text="❄️❄️❄️",
                              font=("Arial", 24),
                              bg="#fafafa")
        snow_label.pack(pady=10)

        # 关闭按钮
        close_btn = tk.Button(popup,
                              text="关闭",
                              command=lambda: self.close_session_summary(popup),
                              font=("Arial", 12, "bold"),
                              bg='#43a047',
                              fg='black',
                              relief=tk.FLAT,
                              padx=10,
                              pady=5,
                              cursor="hand2")
        close_btn.pack(pady=20)

    def close_session_summary(self, popup):
        """关闭弹窗并重置当前 session 的奖项统计"""
        popup.destroy()
        for k in self.prize_counts:
            self.prize_counts[k] = 0

    # --------------------- 管理员入口 ---------------------
    def show_admin_login_dialog(self):
        """管理员入口：输入密码后进入管理员面板"""
        dialog = tk.Toplevel(self.root)
        dialog.title("管理员登录")
        dialog.geometry("300x200")
        dialog.config(bg="#fff8e1")

        label = tk.Label(dialog, text="输入密码进入管理员面板", bg="#fff8e1", font=("Arial", 12))
        label.pack(pady=20)

        password_entry = tk.Entry(dialog, show="*", font=("Arial", 14))
        password_entry.pack(pady=10)

        confirm_button = tk.Button(dialog,
                                   text="确定",
                                   command=lambda: self.check_password(dialog, password_entry),
                                   font=("Arial", 12, "bold"),
                                   bg='#43a047',
                                   fg='black',
                                   relief=tk.FLAT,
                                   padx=10,
                                   pady=5,
                                   cursor="hand2")
        confirm_button.pack(pady=10)

    def check_password(self, dialog, entry):
        """验证管理员密码"""
        pwd = entry.get()
        # 例：假设密码为 'admin'
        if pwd == "admin":
            dialog.destroy()
            self.show_admin_panel()
        else:
            messagebox.showerror("错误", "密码不正确！")

    def show_admin_panel(self):
        """管理员面板：显示财务统计 & 历史记录 (CSV)"""
        admin_window = tk.Toplevel(self.root)
        admin_window.title("管理员面板")
        admin_window.geometry("700x500")
        admin_window.config(bg="#fafafa")

        # 标题
        title_label = tk.Label(admin_window,
                               text="管理员面板",
                               font=("Arial", 18, "bold"),
                               bg="#fafafa",
                               fg='#d32f2f')
        title_label.pack(pady=10)

        # 财务统计区域
        stats_frame = tk.LabelFrame(admin_window, text="财务统计",
                                    font=("Arial", 14, "bold"),
                                    bg="#fafafa",
                                    fg='#1b5e20')
        stats_frame.pack(fill="x", padx=20, pady=10)

        income_label = tk.Label(stats_frame,
                                text=f"总收入：{self.total_income} 元",
                                font=("Arial", 12),
                                bg="#fafafa")
        income_label.pack(anchor="w", padx=10, pady=5)

        payout_label = tk.Label(stats_frame,
                                text=f"总支出：{self.total_payout} 元（不含可乐2元）",
                                font=("Arial", 12),
                                bg="#fafafa")
        payout_label.pack(anchor="w", padx=10, pady=5)

        net_label = tk.Label(stats_frame,
                             text=f"净收入：{self.net_income} 元",
                             font=("Arial", 12),
                             bg="#fafafa")
        net_label.pack(anchor="w", padx=10, pady=5)

        count_label = tk.Label(stats_frame,
                               text=f"游戏总次数：{self.count}",
                               font=("Arial", 12),
                               bg="#fafafa")
        count_label.pack(anchor="w", padx=10, pady=5)

        # 历史记录区域
        history_frame = tk.LabelFrame(admin_window, text="历史记录 (CSV)",
                                      font=("Arial", 14, "bold"),
                                      bg="#fafafa",
                                      fg='#1b5e20')
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)

        text_area = tk.Text(history_frame, wrap="none", font=("Courier New", 10))
        text_area.pack(side="left", fill="both", expand=True)

        # 添加垂直滚动条
        scroll_y = tk.Scrollbar(history_frame, orient="vertical", command=text_area.yview)
        scroll_y.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scroll_y.set)

        # 读取并显示 CSV 内容
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    text_area.insert(tk.END, line)
        else:
            text_area.insert(tk.END, "暂无历史记录。")

        text_area.config(state="disabled")  # 历史记录只读

    # --------------------- 奖项弹窗 ---------------------
    def show_congratulation_window(self):
        """显示大额奖项的庆祝弹窗"""
        popup = tk.Toplevel(self.root)
        popup.title("恭喜！")
        popup.geometry("400x300")
        popup.config(bg="#e1f5fe")

        label = tk.Label(popup,
                         text="🎉 恭喜您赢得大奖！ 🎉",
                         font=("Arial", 20, "bold"),
                         fg="#d32f2f",
                         bg="#e1f5fe")
        label.pack(pady=20)

        # 雪花动画画布
        snow_canvas = tk.Canvas(popup, width=400, height=180, bg="#e1f5fe", highlightthickness=0)
        snow_canvas.pack()

        # 创建雪花
        snowflakes = []
        for i in range(15):
            x = random.randint(0, 400)
            y = random.randint(-200, -20)
            size = random.randint(10, 20)
            flake = snow_canvas.create_text(x, y, text="❄", font=("Arial", size), fill="#90caf9")
            snowflakes.append(flake)

        # 动画函数
        def animate_snowflakes():
            for flake in snowflakes:
                snow_canvas.move(flake, 0, random.randint(2, 5))
                pos = snow_canvas.coords(flake)
                if pos[1] > 200:
                    x = random.randint(0, 400)
                    y = random.randint(-50, -10)
                    snow_canvas.coords(flake, x, y)
            snow_canvas.after(100, animate_snowflakes)

        animate_snowflakes()

    # --------------------- 次数结束后弹窗统计 ---------------------
    def show_session_summary_popup(self):
        """
        当抽奖次数用完后，弹窗显示本 session 各奖项情况，然后重置。
        """
        popup = tk.Toplevel(self.root)
        popup.title("本次抽奖总结")
        popup.geometry("350x450")
        popup.config(bg="#fafafa")

        # 圣诞装饰
        decoration_label = tk.Label(popup,
                                    text="🎄🎉 本次抽奖统计结果 🎉🎄",
                                    font=("Arial", 16, "bold"),
                                    bg="#fafafa",
                                    fg='#d32f2f')
        decoration_label.pack(pady=10)

        # 构造统计字符串
        summary_text = ""
        for k, v in self.prize_counts.items():
            summary_text += f"{k}: {v}\n"

        text_label = tk.Label(popup,
                              text=summary_text.strip(),
                              font=("Arial", 12),
                              bg="#fafafa",
                              justify=tk.LEFT)
        text_label.pack(pady=10)

        # 添加圣诞图片或符号（例如雪花）
        snow_label = tk.Label(popup,
                              text="❄️❄️❄️",
                              font=("Arial", 24),
                              bg="#fafafa")
        snow_label.pack(pady=10)

        # 关闭按钮
        close_btn = tk.Button(popup,
                              text="关闭",
                              command=lambda: self.close_session_summary(popup),
                              font=("Arial", 12, "bold"),
                              bg='#43a047',
                              fg='black',
                              relief=tk.FLAT,
                              padx=10,
                              pady=5,
                              cursor="hand2")
        close_btn.pack(pady=20)

    def close_session_summary(self, popup):
        """关闭弹窗并重置当前 session 的奖项统计"""
        popup.destroy()
        for k in self.prize_counts:
            self.prize_counts[k] = 0

    # --------------------- 管理员入口 ---------------------
    def show_admin_login_dialog(self):
        """管理员入口：输入密码后进入管理员面板"""
        dialog = tk.Toplevel(self.root)
        dialog.title("管理员登录")
        dialog.geometry("300x200")
        dialog.config(bg="#fff8e1")

        label = tk.Label(dialog, text="输入密码进入管理员面板", bg="#fff8e1", font=("Arial", 12))
        label.pack(pady=20)

        password_entry = tk.Entry(dialog, show="*", font=("Arial", 14))
        password_entry.pack(pady=10)

        confirm_button = tk.Button(dialog,
                                   text="确定",
                                   command=lambda: self.check_password(dialog, password_entry),
                                   font=("Arial", 12, "bold"),
                                   bg='#43a047',
                                   fg='black',
                                   relief=tk.FLAT,
                                   padx=10,
                                   pady=5,
                                   cursor="hand2")
        confirm_button.pack(pady=10)

    def check_password(self, dialog, entry):
        """验证管理员密码"""
        pwd = entry.get()
        # 例：假设密码为 'admin'
        if pwd == "admin":
            dialog.destroy()
            self.show_admin_panel()
        else:
            messagebox.showerror("错误", "密码不正确！")

    def show_admin_panel(self):
        """管理员面板：显示财务统计 & 历史记录 (CSV)"""
        admin_window = tk.Toplevel(self.root)
        admin_window.title("管理员面板")
        admin_window.geometry("700x500")
        admin_window.config(bg="#fafafa")

        # 标题
        title_label = tk.Label(admin_window,
                               text="管理员面板",
                               font=("Arial", 18, "bold"),
                               bg="#fafafa",
                               fg='#d32f2f')
        title_label.pack(pady=10)

        # 财务统计区域
        stats_frame = tk.LabelFrame(admin_window, text="财务统计",
                                    font=("Arial", 14, "bold"),
                                    bg="#fafafa",
                                    fg='#1b5e20')
        stats_frame.pack(fill="x", padx=20, pady=10)

        income_label = tk.Label(stats_frame,
                                text=f"总收入：{self.total_income} 元",
                                font=("Arial", 12),
                                bg="#fafafa")
        income_label.pack(anchor="w", padx=10, pady=5)

        payout_label = tk.Label(stats_frame,
                                text=f"总支出：{self.total_payout} 元（不含可乐2元）",
                                font=("Arial", 12),
                                bg="#fafafa")
        payout_label.pack(anchor="w", padx=10, pady=5)

        net_label = tk.Label(stats_frame,
                             text=f"净收入：{self.net_income} 元",
                             font=("Arial", 12),
                             bg="#fafafa")
        net_label.pack(anchor="w", padx=10, pady=5)

        count_label = tk.Label(stats_frame,
                               text=f"游戏总次数：{self.count}",
                               font=("Arial", 12),
                               bg="#fafafa")
        count_label.pack(anchor="w", padx=10, pady=5)

        # 历史记录区域
        history_frame = tk.LabelFrame(admin_window, text="历史记录 (CSV)",
                                      font=("Arial", 14, "bold"),
                                      bg="#fafafa",
                                      fg='#1b5e20')
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)

        text_area = tk.Text(history_frame, wrap="none", font=("Courier New", 10))
        text_area.pack(side="left", fill="both", expand=True)

        # 添加垂直滚动条
        scroll_y = tk.Scrollbar(history_frame, orient="vertical", command=text_area.yview)
        scroll_y.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scroll_y.set)

        # 读取并显示 CSV 内容
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    text_area.insert(tk.END, line)
        else:
            text_area.insert(tk.END, "暂无历史记录。")

        text_area.config(state="disabled")  # 历史记录只读

    # --------------------- 大奖庆祝弹窗 ---------------------
    def show_congratulation_window(self):
        """显示大额奖项的庆祝弹窗"""
        popup = tk.Toplevel(self.root)
        popup.title("恭喜！")
        popup.geometry("400x300")
        popup.config(bg="#e1f5fe")

        label = tk.Label(popup,
                         text="🎉 恭喜您赢得大奖！ 🎉",
                         font=("Arial", 20, "bold"),
                         fg="#d32f2f",
                         bg="#e1f5fe")
        label.pack(pady=20)

        # 雪花动画画布
        snow_canvas = tk.Canvas(popup, width=400, height=180, bg="#e1f5fe", highlightthickness=0)
        snow_canvas.pack()

        # 创建雪花
        snowflakes = []
        for i in range(15):
            x = random.randint(0, 400)
            y = random.randint(-200, -20)
            size = random.randint(10, 20)
            flake = snow_canvas.create_text(x, y, text="❄", font=("Arial", size), fill="#90caf9")
            snowflakes.append(flake)

        # 动画函数
        def animate_snowflakes():
            for flake in snowflakes:
                snow_canvas.move(flake, 0, random.randint(2, 5))
                pos = snow_canvas.coords(flake)
                if pos[1] > 200:
                    x = random.randint(0, 400)
                    y = random.randint(-50, -10)
                    snow_canvas.coords(flake, x, y)
            snow_canvas.after(100, animate_snowflakes)

        animate_snowflakes()

    # --------------------- 运行应用 ---------------------
    def run(self):
        self.root.mainloop()

# ------------------- 启动应用 -------------------
if __name__ == "__main__":
    app = LotteryScratchCard20()
    app.run()