#!/usr/bin/env python3
"""
知识库模块：KnowledgeBase 类
从 knowledge_base.txt 读取问答数据，构建关键词索引和匹配引擎
可独立导入使用

用法:
    from knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    kb.match("什么是深度学习？")
    kb.print_stats()
"""

import os


class KnowledgeBase:
    """知识库：从TXT文件读取问答数据，构建关键词索引和匹配引擎"""

    def __init__(self, filepath=None):
        """初始化知识库，从TXT文件加载数据

        参数:
            filepath: TXT文件路径，默认同目录下的 knowledge_base.txt
        """
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), 'knowledge_base.txt')

        # ① 字典：{问题: 答案}
        self.data = {}

        # ② 每个问题的核心关键词
        self.question_keywords = {}

        # 加载TXT文件
        self._load(filepath)

        # ③ 所有关键词集合（去重）
        self.all_keywords = set()
        for kw_set in self.question_keywords.values():
            self.all_keywords.update(kw_set)

        # ④ 关键词索引：{关键词: [问题, ...]}
        self.keyword_index = {}
        for question, kw_set in self.question_keywords.items():
            for kw in kw_set:
                if kw not in self.keyword_index:
                    self.keyword_index[kw] = []
                self.keyword_index[kw].append(question)

    def _load(self, filepath):
        """解析 TXT 文件，填充 self.data 和 self.question_keywords

        TXT 格式（每条记录4行）:
            Q: 问题
            A: 答案
            K: 关键词1, 关键词2, ...
            ---
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('Q:'):
                question = line[2:].strip()
                # 下一行是 A:
                i += 1
                answer = ''
                while i < len(lines) and not lines[i].strip().startswith('A:'):
                    i += 1
                if i < len(lines):
                    answer = lines[i][2:].strip()
                # 下一行是 K:
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('K:'):
                    i += 1
                keywords = set()
                if i < len(lines):
                    kw_text = lines[i][2:].strip()
                    keywords = set(k.strip() for k in kw_text.split(',') if k.strip())

                self.data[question] = answer
                self.question_keywords[question] = keywords

            i += 1

    # ---------- 公开方法 ----------

    def get_answer(self, question):
        """根据问题返回答案"""
        return self.data.get(question, None)

    def get_keywords(self, question):
        """返回某个问题的关键词集合"""
        return self.question_keywords.get(question, set())

    def get_questions_by_keyword(self, keyword):
        """返回包含该关键词的所有问题"""
        return self.keyword_index.get(keyword, [])

    def get_all_questions(self):
        """返回所有问题列表"""
        return list(self.data.keys())

    def total_questions(self):
        return len(self.data)

    def total_keywords(self):
        return len(self.all_keywords)

    def extract_keywords(self, text):
        """从用户输入中提取知识库中已有的关键词 -> 集合"""
        found = set()
        for kw in self.all_keywords:
            if kw in text:
                found.add(kw)
        return found

    def match(self, user_input):
        """关键词匹配：返回 (问题, 答案, 匹配关键词数)

        遍历知识库，对每个问题计算用户关键词与问题关键词的交集，
        取交集最大的问题作为最佳匹配。
        """
        user_kw = self.extract_keywords(user_input)
        if not user_kw:
            return None, "抱歉，未找到相关答案，请尝试其他问题。", 0
        best_q = None
        best_cnt = 0
        for question in self.data:
            q_kw = self.question_keywords.get(question, set())
            intersection = user_kw & q_kw
            cnt = len(intersection)
            if cnt > best_cnt:
                best_cnt = cnt
                best_q = question
        if best_q and best_cnt > 0:
            return best_q, self.data[best_q], best_cnt
        else:
            return None, "抱歉，未找到相关答案，请尝试其他问题。", 0

    def print_stats(self):
        """控制台输出知识库统计（截图用）"""
        import sys
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
        print("=" * 60)
        print("[知识库统计]")
        print("=" * 60)
        print(f"  总问题数: {self.total_questions()}")
        print(f"  总关键词数(去重): {self.total_keywords()}")
        print(f"  关键词索引条目: {len(self.keyword_index)}")
        print()
        print("[问题列表]:")
        for i, q in enumerate(self.data, 1):
            kws = ", ".join(self.question_keywords[q])
            print(f"  {i:2d}. {q}")
            print(f"     关键词: {{{kws}}}")
        print()
        print("[关键词分类统计]:")
        for kw in sorted(self.all_keywords):
            questions = self.keyword_index[kw]
            print(f"  [{kw}] -> {len(questions)} 个问题")
        print("=" * 60)


if __name__ == "__main__":
    # 独立测试
    kb = KnowledgeBase()
    kb.print_stats()
    print()
    # 测试匹配
    for test in ["什么是深度学习", "Python AI", "CNN RNN", "不相关的话题"]:
        q, a, n = kb.match(test)
        if q:
            print(f'  "{test}" -> {q} (匹配{n}个关键词)')
        else:
            print(f'  "{test}" -> 未匹配')
