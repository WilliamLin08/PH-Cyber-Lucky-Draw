import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import csv
import os
from datetime import datetime

class LotteryScratchCard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("刮刮乐 - 圣诞特别版")
        self.root.geometry("600x850")

        # 设置浅绿色背景
        self.root.configure(bg='#e8f5e9')

        # 奖项设置
        self.prizes = {
            "特等奖 (100元)": 0.002,
            "一等奖 (50元)": 0.01,
            "二等奖 (20元)": 0.03,
            "三等奖 (10元)": 0.08,
            "四等奖 (2元)": 0.22,
            "再来一次": 0.10,
            "未中奖": 0.558
        }

        # 奖项对应的金额
        self.prize_values = {
            "特等奖 (100元)": 100,
            "一等奖 (50元)": 50,
            "二等奖 (20元)": 20,
            "三等奖 (10元)": 10,
            "四等奖 (2元)": 2,  # 不计入支出
            "再来一次": 0,
            "未中奖": 0
        }

        # 保底机制计数器
        self.consecutive_losses = 0
        self.guaranteed_win = 12  # 连续12次未中奖后保底

        # 刮开区域追踪
        self.scratch_matrix = None
        self.revealed = False
        self.canvas_width = 500
        self.canvas_height = 300
        self.matrix_scale = 1  # 每个像素一个计数单位

        # 财务指标
        self.total_income = 0   # 总收入
        self.total_payout = 0   # 总支出（不包含四等奖）
        self.net_income = 0     # 净收入
        self.count = 0          # 游戏总次数

        # 抽奖次数
        self.allowed_plays = 0  # 初始为0，需手动输入

        # 标记是否持有“再来一次”的免费游戏资格
        self.is_free_game = False

        # 用于统计“当前这次可玩次数”内，各个奖项的抽中数量
        self.prize_counts = {
            "特等奖 (100元)": 0,
            "一等奖 (50元)": 0,
            "二等奖 (20元)": 0,
            "三等奖 (10元)": 0,
            "四等奖 (2元)": 0,
            "再来一次": 0,
            "未中奖": 0
        }

        # CSV文件路径
        self.csv_file = "lottery_results.csv"
        self.initialize_csv()

        # 创建主界面
        self.create_widgets()

        # 绑定空格键到开始新游戏，但只有当allowed_plays > 0时才能开始
        self.root.bind('<space>', lambda event: self.start_new_game(charge=True))

        # 给“一键刮开”按钮绑定按键 (示例使用 "r")
        self.root.bind('<r>', lambda event: self.reveal_all())

    def initialize_csv(self):
        """初始化CSV文件，如果不存在则创建并写入表头。"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Prize", "Income (元)", "Payout (元)", "Net Income (元)"])

    def create_widgets(self):
        # 圣诞祝福语
        christmas_label = tk.Label(self.root,
                                   text="❄  Merry Christmas  ❄\n    🎄  Ho Ho Ho~  🎄",
                                   font=("Brush Script MT", 34, "italic"),
                                   fg='#c62828',  # 深红色文字
                                   bg='#e8f5e9')
        christmas_label.pack(pady=15)

        # 标题标签
        title_label = tk.Label(self.root, text="刮刮乐彩票 - 圣诞欢乐场",
                               font=("Arial", 24, "bold"),
                               fg='#1b5e20',  # 深绿色
                               bg='#e8f5e9')
        title_label.pack(pady=10)

        # 按钮框架
        button_frame = tk.Frame(self.root, bg='#e8f5e9')
        button_frame.pack(pady=10)

        # 开始按钮
        self.start_button = tk.Button(button_frame, text="开始新游戏 (空格)",
                                      command=lambda: self.start_new_game(charge=True),
                                      font=("Arial", 14, "bold"),
                                      bg='#43a047',  # 绿色按钮
                                      fg='black',
                                      relief=tk.FLAT,
                                      padx=15,
                                      pady=5,
                                      cursor="hand2")
        self.start_button.pack(side=tk.LEFT, padx=15)

        # 一键刮开按钮
        self.reveal_button = tk.Button(button_frame, text="一键刮开 (按 R)",
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
        self.setup_plays_button = tk.Button(button_frame, text="设置抽奖次数",
                                            command=self.show_set_plays_dialog,
                                            font=("Arial", 14, "bold"),
                                            bg='#fdd835',  # 金黄色
                                            fg='black',
                                            relief=tk.FLAT,
                                            padx=15,
                                            pady=5,
                                            cursor="hand2")
        self.setup_plays_button.pack(side=tk.LEFT, padx=15)

        # 画布框架
        self.frame = tk.Frame(self.root, bg='#e8f5e9')
        self.frame.pack(pady=20)

        # 画布
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

        # 显示游戏总次数
        info_frame = tk.Frame(self.root, bg='#e8f5e9')
        info_frame.pack(pady=10)

        self.game_count_label = tk.Label(info_frame,
                                         text="游戏总次数: 0",
                                         font=("Arial", 14),
                                         bg='#e8f5e9',
                                         fg='#0277bd')
        self.game_count_label.pack(side=tk.LEFT, padx=10)

        # 剩余可玩次数标签
        self.remaining_plays_label = tk.Label(self.root,
                                              text="剩余可玩次数: 未设置",
                                              font=("Arial", 14),
                                              bg='#e8f5e9',
                                              fg='#0277bd')
        self.remaining_plays_label.pack(pady=10)

        # ---- 不再显示奖项统计的窗口，故删除此处的 prize_summary_frame ----

        # 管理员入口放置在右上角
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

        # 按钮悬停效果
        self.setup_button_hover()
        # 初始化开始按钮状态
        self.update_start_button_state()

    def setup_button_hover(self):
        """设置按钮悬停效果"""
        def on_enter(e):
            btn = e.widget
            if btn == self.admin_button:
                e.widget['background'] = '#ffeb3b'
            elif btn == self.setup_plays_button:
                e.widget['background'] = '#ffd54f'
            else:
                e.widget['background'] = '#66bb6a'

        def on_leave(e):
            btn = e.widget
            if btn == self.admin_button:
                e.widget['background'] = '#f9a825'
            elif btn == self.setup_plays_button:
                e.widget['background'] = '#fdd835'
            elif btn == self.reveal_button or btn == self.start_button:
                e.widget['background'] = '#43a047'

        for btn in [self.start_button, self.reveal_button, self.setup_plays_button, self.admin_button]:
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def update_start_button_state(self):
        """
        根据 self.allowed_plays 是否大于 0，决定是否启用 "开始新游戏" 按钮。
        """
        if self.allowed_plays > 0:
            self.start_button.config(state=tk.NORMAL)
            self.remaining_plays_label.config(text=f"剩余可玩次数: {self.allowed_plays}")
        else:
            self.start_button.config(state=tk.DISABLED)
            if self.allowed_plays == 0:
                self.remaining_plays_label.config(text="剩余可玩次数: 0")

    def show_set_plays_dialog(self):
        """
        弹窗让玩家手动输入可玩次数。
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("设置抽奖次数")
        dialog.geometry("300x150")
        dialog.config(bg="#fff8e1")

        label = tk.Label(dialog, text="请输入抽奖次数：", bg="#fff8e1", font=("Arial", 12))
        label.pack(pady=10)

        entry = tk.Entry(dialog, font=("Arial", 12))
        entry.pack(pady=5)

        confirm_button = tk.Button(dialog, text="确定",
                                   command=lambda: self.confirm_plays(dialog, entry),
                                   font=("Arial", 12, "bold"),
                                   bg='#43a047',
                                   fg='black',
                                   relief=tk.FLAT,
                                   padx=10,
                                   pady=5,
                                   cursor="hand2")
        confirm_button.pack()

    def confirm_plays(self, dialog, entry):
        """
        确认输入的抽奖次数，并更新 allowed_plays。
        同时重置当前 session 的奖项统计。
        """
        val = entry.get()
        try:
            val = int(val)
        except ValueError:
            messagebox.showerror("错误", "请输入数字！")
            return

        if val <= 0:
            messagebox.showerror("错误", "抽奖次数必须为正数！")
        else:
            self.allowed_plays = val
            dialog.destroy()

            # 每次重新设置抽奖次数时，把当前session的奖项统计清零
            for k in self.prize_counts:
                self.prize_counts[k] = 0

            self.update_start_button_state()

    def start_new_game(self, charge=True):
        """
        当点击开始游戏时，如果 allowed_plays > 0，才可以真正开始。
        当玩家持有 "再来一次" 的免费游戏资格时，本次抽奖不扣减次数。
        """
        if self.is_free_game:
            charge = False
            self.is_free_game = False

        if self.allowed_plays <= 0 and charge:
            messagebox.showwarning("提醒", "当前抽奖次数已用完，请重新设置抽奖次数。")
            return

        # 如果按钮被禁用，直接返回
        if str(self.start_button['state']) == 'disabled':
            return

        # 临时禁用按钮防止重复点击
        self.start_button.config(state=tk.DISABLED)

        if charge:
            # 增加收入（每张刮刮卡 5元）
            self.total_income += 5
            # 减少 1 次可玩次数
            self.allowed_plays -= 1
            self.update_start_button_state()

        # 重置刮开区域追踪
        self.scratch_matrix = np.zeros((self.canvas_height // self.matrix_scale,
                                        self.canvas_width // self.matrix_scale))
        self.revealed = False

        # 显示画布框架
        self.frame.pack(pady=20)
        self.canvas.delete("all")

        # 启用一键刮开按钮
        self.reveal_button.config(state=tk.NORMAL)

        # 决定中奖结果
        self.current_prize = self.determine_prize()

        # 创建奖项文字
        self.canvas.create_text(self.canvas_width // 2, self.canvas_height // 2,
                                text=self.current_prize,
                                font=("Arial", 36, "bold"),
                                fill="#d32f2f" if "奖" in self.current_prize else "#455a64",
                                tags="prize")

        # 创建灰色覆盖层
        self.create_scratch_layer()

        # 绑定鼠标事件
        self.canvas.bind("<B1-Motion>", self.scratch)
        self.canvas.bind("<Button-1>", self.scratch)

        # 当抽奖次数用完后，弹窗显示当前session的奖项汇总
        if self.allowed_plays == 0 and not self.is_free_game:
            self.show_session_summary_popup()

        self.root.after(500, lambda: self.update_start_button_state())

    def show_session_summary_popup(self):
        """
        当抽奖次数用完之后，弹出一个窗口，显示本次session内所获奖项的数量。
        随后将统计清零。
        """
        popup = tk.Toplevel(self.root)
        popup.title("本次抽奖总结")
        popup.geometry("300x400")
        popup.config(bg="#fafafa")

        label = tk.Label(popup, text="本次抽奖统计结果", font=("Arial", 14, "bold"), bg="#fafafa")
        label.pack(pady=10)

        # 构造统计字符串
        summary_text = ""
        for k, v in self.prize_counts.items():
            summary_text += f"{k}: {v}\n"

        text_label = tk.Label(popup, text=summary_text.strip(), font=("Arial", 12), bg="#fafafa")
        text_label.pack(pady=5)

        # 关闭按钮
        close_btn = tk.Button(popup, text="关闭",
                              command=lambda: self.close_session_summary(popup),
                              font=("Arial", 12, "bold"),
                              bg='#43a047',
                              fg='black',
                              relief=tk.FLAT,
                              padx=10,
                              pady=5,
                              cursor="hand2")
        close_btn.pack(pady=10)

    def close_session_summary(self, popup):
        """
        关闭弹窗，并重置当前 session 的奖项统计数据
        """
        popup.destroy()
        for k in self.prize_counts:
            self.prize_counts[k] = 0

    def reveal_all(self):
        # 如果按钮被禁用，直接返回
        if str(self.reveal_button['state']) == 'disabled':
            return
        self.canvas.delete("scratch")
        self.revealed = True
        self.reveal_button.config(state=tk.DISABLED)

    def create_scratch_layer(self):
        rect_size = 12
        for x in range(0, self.canvas_width, rect_size):
            for y in range(0, self.canvas_height, rect_size):
                self.canvas.create_rectangle(x, y, x + rect_size, y + rect_size,
                                             fill='#9e9e9e',
                                             outline='#9e9e9e',
                                             tags="scratch")

    def determine_prize(self):
        # 检查是否需要保底
        if self.consecutive_losses >= self.guaranteed_win:
            self.consecutive_losses = 0
            prize = "二等奖 (20元)"
            self.update_payout(prize)
            self.log_result(prize)
            self.update_game_count()
            self.check_big_prize_popup(prize)
            return prize

        # 随机抽取奖项
        rand_num = random.random()
        cumulative_prob = 0

        for prize, prob in self.prizes.items():
            cumulative_prob += prob
            if rand_num <= cumulative_prob:
                if prize == "再来一次":
                    self.is_free_game = True
                    self.update_payout(prize)
                    self.log_result(prize)
                    self.update_game_count()
                    return prize

                # 更新连续未中奖计数器
                if prize in ["特等奖 (100元)", "一等奖 (50元)", "二等奖 (20元)"]:
                    self.consecutive_losses = 0
                else:
                    self.consecutive_losses += 1

                self.update_payout(prize)
                self.log_result(prize)
                self.update_game_count()
                self.check_big_prize_popup(prize)
                return prize

        # 默认返回"未中奖"
        self.log_result("未中奖")
        self.consecutive_losses += 1
        return "未中奖"

    def update_game_count(self):
        self.count += 1
        self.game_count_label.config(text=f"游戏总次数: {self.count}")

    def update_payout(self, prize):
        if prize == "四等奖 (2元)":
            payout = 0
        else:
            payout = self.prize_values.get(prize, 0)
        self.total_payout += payout
        self.update_financial_metrics()

    def update_financial_metrics(self):
        self.net_income = self.total_income - self.total_payout

    def log_result(self, prize):
        """
        记录结果到 CSV，并更新当前 session 的奖项统计
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payout_record = 0 if prize == "四等奖 (2元)" else self.prize_values.get(prize, 0)
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                prize,
                self.total_income,
                payout_record,
                self.net_income
            ])

        # 这里更新奖项统计，但不在主界面显示
        if prize in self.prize_counts:
            self.prize_counts[prize] += 1

    def scratch(self, event):
        x, y = event.x, event.y
        r = 25
        overlapping = self.canvas.find_overlapping(x - r, y - r, x + r, y + r)
        for item in overlapping:
            if "scratch" in self.canvas.gettags(item):
                self.canvas.delete(item)
        matrix_x = min(y // self.matrix_scale, self.scratch_matrix.shape[0] - 1)
        matrix_y = min(x // self.matrix_scale, self.scratch_matrix.shape[1] - 1)

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                new_x = int(matrix_x + dx)
                new_y = int(matrix_y + dy)
                if (0 <= new_x < self.scratch_matrix.shape[0] and
                        0 <= new_y < self.scratch_matrix.shape[1]):
                    self.scratch_matrix[new_x, new_y] = 1

        scratched_percentage = np.sum(self.scratch_matrix) / self.scratch_matrix.size
        if scratched_percentage > 0.3 and not self.revealed:
            self.revealed = True
            self.reveal_button.config(state=tk.DISABLED)

    def check_big_prize_popup(self, prize):
        if prize in ["特等奖 (100元)", "一等奖 (50元)"]:
            self.show_congratulation_window()

    def show_congratulation_window(self):
        popup = tk.Toplevel(self.root)
        popup.title("Congratulation!")
        popup.geometry("400x300")
        popup.config(bg="#e1f5fe")

        label = tk.Label(popup, text="Congratulation!\nYou Won BIG Prize!",
                         font=("Arial", 20, "bold"),
                         fg="#d32f2f",
                         bg="#e1f5fe")
        label.pack(pady=20)

        self.snow_canvas = tk.Canvas(popup, width=400, height=180, bg="#e1f5fe", highlightthickness=0)
        self.snow_canvas.pack()

        self.snowflakes = []
        for i in range(15):
            x = random.randint(0, 400)
            y = random.randint(-200, -20)
            size = random.randint(10, 20)
            flake = self.snow_canvas.create_text(x, y, text="❄", font=("Arial", size), fill="#90caf9")
            self.snowflakes.append(flake)

        self.animate_snowflakes()

    def animate_snowflakes(self):
        if not hasattr(self, 'snow_canvas') or self.snow_canvas is None:
            return
        for flake in self.snowflakes:
            self.snow_canvas.move(flake, 0, random.randint(2, 5))
            pos = self.snow_canvas.coords(flake)
            if pos[1] > 200:
                x = random.randint(0, 400)
                y = random.randint(-50, -10)
                self.snow_canvas.coords(flake, x, y)
        self.snow_canvas.after(100, self.animate_snowflakes)

    # ----------------  管理员入口相关逻辑  ----------------- #
    def show_admin_login_dialog(self):
        """管理员入口：输入密码后进入管理员面板"""
        dialog = tk.Toplevel(self.root)
        dialog.title("管理员登录")
        dialog.geometry("300x150")
        dialog.config(bg="#fff8e1")

        label = tk.Label(dialog, text="输入密码进入管理员面板", bg="#fff8e1", font=("Arial", 12))
        label.pack(pady=10)

        password_entry = tk.Entry(dialog, show="*", font=("Arial", 12))
        password_entry.pack(pady=5)

        confirm_button = tk.Button(dialog, text="确定",
                                   command=lambda: self.check_password(dialog, password_entry),
                                   font=("Arial", 12, "bold"),
                                   bg='#43a047',
                                   fg='black',
                                   relief=tk.FLAT,
                                   padx=10,
                                   pady=5,
                                   cursor="hand2")
        confirm_button.pack()

    def check_password(self, dialog, entry):
        pwd = entry.get()
        # 假设密码为 'admin'
        if pwd == "admin":
            dialog.destroy()
            self.show_admin_panel()
        else:
            messagebox.showerror("错误", "密码不正确！")

    def show_admin_panel(self):
        """管理员面板：显示财务统计、当前连续未中奖次数和历史记录"""
        admin_window = tk.Toplevel(self.root)
        admin_window.title("管理员面板")
        admin_window.geometry("600x400")
        admin_window.config(bg="#fafafa")

        title_label = tk.Label(admin_window, text="管理员面板",
                               font=("Arial", 16, "bold"), bg="#fafafa")
        title_label.pack(pady=10)

        # 财务统计区域
        stats_frame = tk.LabelFrame(admin_window, text="财务统计",
                                    font=("Arial", 12, "bold"), bg="#fafafa")
        stats_frame.pack(fill="x", padx=10, pady=5)

        income_label = tk.Label(stats_frame, text=f"总收入：{self.total_income} 元",
                                font=("Arial", 12), bg="#fafafa")
        income_label.pack(anchor="w", padx=10, pady=2)

        payout_label = tk.Label(stats_frame, text=f"总支出：{self.total_payout} 元（不含四等奖）",
                                font=("Arial", 12), bg="#fafafa")
        payout_label.pack(anchor="w", padx=10, pady=2)

        net_label = tk.Label(stats_frame, text=f"净收入：{self.net_income} 元",
                             font=("Arial", 12), bg="#fafafa")
        net_label.pack(anchor="w", padx=10, pady=2)

        count_label = tk.Label(stats_frame, text=f"游戏总次数：{self.count}",
                               font=("Arial", 12), bg="#fafafa")
        count_label.pack(anchor="w", padx=10, pady=2)

        # 在管理员面板显示当前连续未中奖次数
        consecutive_label = tk.Label(stats_frame,
                                     text=f"当前连续未中奖次数：{self.consecutive_losses}",
                                     font=("Arial", 12),
                                     bg="#fafafa")
        consecutive_label.pack(anchor="w", padx=10, pady=2)

        # 历史记录区域
        history_frame = tk.LabelFrame(admin_window, text="历史记录 (CSV)",
                                      font=("Arial", 12, "bold"), bg="#fafafa")
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        text_area = tk.Text(history_frame, wrap="none", font=("Courier New", 10))
        text_area.pack(side="left", fill="both", expand=True)

        scroll_y = tk.Scrollbar(history_frame, orient="vertical", command=text_area.yview)
        scroll_y.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scroll_y.set)

        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    text_area.insert(tk.END, line)
        else:
            text_area.insert(tk.END, "暂无历史记录。")

        text_area.config(state="disabled")  # 历史记录只读

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LotteryScratchCard()
    app.run()