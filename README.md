# 人工智能基础问答系统 — 实验三

## 文件说明

| 文件 | 作用 | 说明 |
|---|---|---|
| `main.py` | GUI主程序 | 双击运行，对话界面 |
| `knowledge_base.py` | 知识库类模块 | 解析TXT、构建索引、关键词匹配 |
| `knowledge_base.txt` | 纯文本知识库 | 🔑 存储问题和答案，可直接编辑扩充 |
| `实验报告_人工智能基础问答系统.docx` | 实验报告 | 按模板填写，含截图位置 |
| `实验要求.txt` | 原题说明 | — |

## 运行方式

```bash
python main.py
```

需要 Python 3.9+，无需安装第三方库。

## 如何扩展知识库

用记事本打开 `knowledge_base.txt`，在末尾追加：

```text
Q: 你想新增的问题？
A: 对应的答案...
K: 关键词1, 关键词2, 关键词3
---
```

保存后重新运行程序即可生效。

## 文件架构

```
knowledge_base.txt (数据层)
     ↓ 读取
knowledge_base.py (逻辑层: 解析+索引+匹配)
     ↓ import
main.py (表现层: GUI+交互)
```

## 版本管理（Git + GitHub）

```bash
git init
git add .
git commit -m "完成AI问答系统"
git remote add origin https://github.com/你的用户名/ai-qa-system.git
git push -u origin main
```
