#!/usr/bin/env python3
"""
实验三：小型人工智能基础问答系统
功能：知识库构建 / 关键词匹配 / 可视化交互 / 提问记录
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import re

# ============================================================
#  KnowledgeBase 类（知识库 + 关键词索引 + 匹配引擎）
# ============================================================

from knowledge_base import KnowledgeBase

class QASystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("实验三：人工智能基础问答系统")
        self.geometry("800x620")
        self.minsize(650, 500)

        self.kb = KnowledgeBase()  # 知识库
        self.history = []          # 提问记录列表
        self.configure(bg='#f0f0f0')

        self._build_ui()

        # 显示欢迎信息
        self._show_bot("你好！我是AI基础问答助手。\n请输入你关于人工智能的问题，输入「退出」结束对话。")

    def _build_ui(self):
        # ========== grid 3行布局：标题 / 对话区 / 底部面板 ==========
        self.grid_rowconfigure(1, weight=1)   # 第1行(对话区)可伸缩
        self.grid_columnconfigure(0, weight=1)  # 整个窗口宽度可伸缩

        # ---- 第0行：标题栏 ----
        title_f = tk.Frame(self, bg='#2c3e50', height=50)
        title_f.grid(row=0, column=0, sticky='ew')
        title_f.grid_propagate(False)
        tk.Label(title_f, text="🤖 AI基础问答系统", bg='#2c3e50', fg='white',
                 font=('TkDefaultFont', 16, 'bold')).pack(expand=True)

        # ---- 第2行：底部面板（固定高度，输入框在上+状态栏在下）----
        bottom_f = tk.Frame(self, bg='#f0f0f0')
        bottom_f.grid(row=2, column=0, sticky='ew')
        bottom_f.grid_columnconfigure(0, weight=1)

        # 底部面板内部 grid 2行：输入行(0) / 状态行(1)
        # --- 输入行 ---
        input_f = tk.Frame(bottom_f, bg='#f0f0f0')
        input_f.grid(row=0, column=0, sticky='ew', padx=12, pady=(6, 2))
        input_f.grid_columnconfigure(0, weight=1)

        self.entry = tk.Entry(input_f, font=('TkDefaultFont', 12), relief=tk.SOLID, borderwidth=1)
        self.entry.grid(row=0, column=0, sticky='ew', ipady=6, padx=(0, 5))
        self.entry.bind('<Return>', lambda e: self._send())
        self.entry.focus()

        send_btn = tk.Button(input_f, text=" 发送 ", command=self._send,
                             bg='#3498db', fg='white', font=('TkDefaultFont', 11, 'bold'),
                             relief=tk.FLAT, padx=15, cursor='hand2')
        send_btn.grid(row=0, column=1)

        # --- 状态行 ---
        stat_f = tk.Frame(bottom_f, bg='#ecf0f1', height=30)
        stat_f.grid(row=1, column=0, sticky='ew')
        stat_f.grid_propagate(False)
        stat_f.grid_columnconfigure(1, weight=1)

        self.stat_label = tk.Label(stat_f, text="💡 输入问题获取答案 | 输入「退出」结束对话",
                                    bg='#ecf0f1', fg='#7f8c8d', font=('TkDefaultFont', 9))
        self.stat_label.grid(row=0, column=0, padx=8, sticky='w')
        self.cnt_label = tk.Label(stat_f, text="提问次数: 0", bg='#ecf0f1',
                                   fg='#2c3e50', font=('TkDefaultFont', 9, 'bold'))
        self.cnt_label.grid(row=0, column=2, padx=8, sticky='e')

        # ---- 第1行：对话记录（中间，自动伸缩撑满）----
        chat_f = tk.Frame(self, bg='#f0f0f0')
        chat_f.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        chat_f.grid_rowconfigure(0, weight=1)
        chat_f.grid_columnconfigure(0, weight=1)

        self.chat_box = tk.Text(chat_f, font=('TkDefaultFont', 11), wrap=tk.WORD,
                                state=tk.DISABLED, bg='white', relief=tk.FLAT,
                                padx=10, pady=10, spacing1=4, spacing2=2)
        self.chat_box.grid(row=0, column=0, sticky='nsew')

        scroll = ttk.Scrollbar(chat_f, command=self.chat_box.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.chat_box.configure(yscrollcommand=scroll.set)

        # 配置对话标签颜色
        self.chat_box.tag_config("user", foreground="#2c3e50", font=('TkDefaultFont', 11, 'bold'))
        self.chat_box.tag_config("bot", foreground="#27ae60", font=('TkDefaultFont', 11))
        self.chat_box.tag_config("error", foreground="#e74c3c", font=('TkDefaultFont', 11))
        self.chat_box.tag_config("info", foreground="#7f8c8d", font=('TkDefaultFont', 10))

    def _show_user(self, msg):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"🧑 你：", "user")
        self.chat_box.insert(tk.END, f"{msg}\n\n", "user")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def _show_bot(self, msg):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"🤖 助手：", "bot")
        self.chat_box.insert(tk.END, f"{msg}\n\n", "bot")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def _show_info(self, msg):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"{msg}\n", "info")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def _send(self):
        user_input = self.entry.get().strip()
        if not user_input:
            return

        # 清空输入框
        self.entry.delete(0, tk.END)

        # 记录历史
        self.history.append(user_input)

        # 显示用户输入
        self._show_user(user_input)

        # 检查退出
        if user_input == "退出":
            self._show_bot("感谢使用！本次对话已结束。")
            self._show_info(f"📊 共提问 {len(self.history)} 次")
            self.entry.config(state=tk.DISABLED)
            self.stat_label.config(text="对话已结束")
            self._update_count()
            return

        # 匹配答案
        question, answer, match_cnt = self.kb.match(user_input)

        if question:
            # 显示匹配到的关键词数量
            self._show_info(f"  匹配到 {match_cnt} 个关键词 → 《{question}》")
            self._show_bot(answer)
        else:
            self._show_bot(answer)

        self._update_count()

    def _update_count(self):
        self.cnt_label.config(text=f"提问次数: {len(self.history)}")


# ============================================================
#  信息展示
# ============================================================

def print_knowledge_base_info():
    """控制台输出知识库统计（截图用）"""
    import sys
    # Windows GBK 控制台无法显示 emoji，先尝试设置 UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("=" * 60)
    print("[知识库统计]")
    print("=" * 60)
    print(f"  总问题数: {len(KNOWLEDGE_BASE)}")
    print(f"  总关键词数(去重): {len(ALL_KEYWORDS)}")
    print(f"  关键词索引条目: {len(KEYWORD_INDEX)}")
    print()

    print("[问题列表]:")
    for i, q in enumerate(KNOWLEDGE_BASE, 1):
        kws = ", ".join(QUESTION_KEYWORDS[q])
        print(f"  {i:2d}. {q}")
        print(f"     关键词: {{{kws}}}")
    print()

    print("[关键词分类统计]:")
    for kw in sorted(ALL_KEYWORDS):
        questions = KEYWORD_INDEX[kw]
        print(f"  [{kw}] -> {len(questions)} 个问题")
    print("=" * 60)


if __name__ == "__main__":
    # 控制台输出知识库统计（截图用）
    kb = KnowledgeBase()
    kb.print_stats()
    # 启动 GUI
    app = QASystem()
    app.mainloop()
