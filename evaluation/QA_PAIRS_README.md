# 问答对评测集（QA Pairs v1）

用于流程 3（可追溯问答）和检索评测的可复现数据。

## 文件

- `datasets/qa_pairs_v1.schema.json`：字段规范。
- `datasets/qa_pairs_v1.synthetic.json`：当前生成的合成种子，全部标记 `synthetic: true`。
- 生成脚本：`scripts/generate_qa_pairs.py`。

## 生成命令

```powershell
.venv\Scripts\python.exe scripts\generate_qa_pairs.py --count 30
```

## 真实数据要求

真实学习资料授权到位后：

1. 使用真实文件生成问答对。
2. `synthetic` 必须设为 `false`。
3. `gold_chunk_ids` 必须指向真实 `document_chunks.chunk_id`。
4. 人工标注答案质量后才可标记 `status: approved`。

未授权前，任何真实数据结论都不得从合成集推导。
