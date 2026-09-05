# FileMate 真实用户评测执行协议

## 目标

用真实但匿名的数据回答四组问题：检索引用是否可靠、按需多 Agent 是否优于单 Agent、多模态面试是否提升训练质量、学习伙伴反馈是否促进执行。演示数据和示例 CSV 不计入正式结果。

## 最小样本

- 30 名大学生，覆盖至少 3 个专业。
- 100 份已获授权的课程资料。
- 至少 300 次检索引用相关性标注。
- 每名学生完成一次 20 分钟任务和前后测；对照实验每个条件至少 15 人。

## 四组实验设计

| 研究问题 | A 组 | B 组 | 主要指标 | 必须控制 |
| --- | --- | --- | --- | --- |
| 检索引用是否可靠 | 整篇截断/基础检索 | FileMate 分块检索 | Recall@1/3、MRR、引用正确率、响应时间 | 同一资料、同一问题、相同设备 |
| 多 Agent 是否有效 | 单 Agent 完成全部任务 | 按需调用规划/资料/教练/评价/安全角色 | 任务完成率、幻觉率、耗时、调用数、成本 | 同一模型、提示预算与任务顺序随机 |
| 多模态面试是否有效 | 文字回答 | 摄像头本地录像 + 语音回答 | 完成率、复练提升、导师盲评、系统—导师相关性、停顿与语速 | 不做颜值、情绪或性格判断 |
| 学习伙伴是否促进坚持 | 普通文字提醒 | 由真实学习证据驱动的形象反馈 | 任务完成率、到期复习率、次日返回率 | 不用羞辱文案，不用虚假成长值 |

参与者按匿名编号随机分组。面试由两名教师或企业导师盲评；标注分歧先保留，再由第三人裁决。摄像头录像默认只存在参与者浏览器内存，研究表只记录分数和行为计数，不收集原始视频或逐字稿。

## 单次流程

1. 告知参与者数据默认保存在本机，可随时退出；禁止上传身份证、联系方式、成绩单等敏感资料。
2. 参与者导入一份自己的课程资料，完成一次检索、一次练习和一次今日学习任务。
3. 对检索引用点击“相关”或“不相关”。系统只保存目标哈希、排名、检索分数、问题长度和评分。
4. 记录任务是否完成、耗时、前后测得分及 SUS 问卷；使用随机参与者编号，不记录姓名和学号。
5. 在“成长数据”导出匿名 CSV，用 `evaluation/analyze_feedback.py` 生成统计报告。
6. 多 Agent、面试和学习伙伴实验分别复制三个 `.template.csv`，只填匿名编号和数值字段；禁止写姓名、学号、文件名、问题原文或回答原文。

## 命令

```powershell
python evaluation/analyze_feedback.py filemate-anonymous-feedback.csv --sample-kind real --output _working/real-feedback-report.json
python evaluation/analyze_study.py --annotations evaluation/datasets/retrieval_annotations.csv --study evaluation/datasets/user_study.csv --output _working/real-user-study-report.json
python evaluation/analyze_competition_trials.py --agent evaluation/datasets/agent_ab.csv --interview evaluation/datasets/interview_ab.csv --companion evaluation/datasets/companion_ab.csv --output _working/competition-trials-report.json
```

## 通过门槛

- 检索引用正向率不低于 75%，同时报告 95% Wilson 区间。
- 前后测平均提升不低于 15%。
- 平均节省时间不低于 20%。
- SUS 不低于 70。
- 所有正式结论必须标注样本量、日期和“真实/合成”属性，不得用示例数据冒充实测结果。
- 多 Agent：任务完成率提高、幻觉率下降；同时完整报告耗时、模型调用数和成本，不能只报优势。
- 多模态面试：系统分与双导师均分的相关性达到 0.70 以上，并报告平均绝对误差；样本不足时显示“待评测”。
- 学习伙伴：到期复习完成率或次日返回率有提升；未达到每组 15 人前不得宣称有效。
