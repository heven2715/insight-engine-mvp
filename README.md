⚡ Insight Engine - 全流程增长归因与 A/B 测试实验看板
🚀 项目简介
Insight Engine 是一款专为增长分析师（DA）和增长运营设计的自动化归因工具。它旨在解决业务中频繁变动的分析口径问题，通过参数化建模和自动化统计检验，帮助团队快速从原始日志中发现增长机会并规避统计归因陷阱（如辛普森悖论）。

本项目完全采用 AI 原生开发流 (AI-Native Workflow / Vibe Coding) 构建，体现了在 AI 时代下，“需求定义 + 逻辑架构 + AI 实现”的极效生产力。

✨ 核心功能
1. 全链路转化漏斗建模 (Dynamic Funnel)
多级漏斗追踪：自定义 注册 -> 激活 -> 留存 -> 转化 的完整分析路径。

参数化激活口径：支持实时调整“有效激活”的时间门槛（如 1-7 天），动态观察不同活跃深度对后端留存的影响。

2. 自动化 A/B 测试归因 (Statistical Validation)
显著性检验：集成 scipy.stats 模块，针对实验组与对照组进行 卡方检验 (Chi-Square Test)，自动化输出 P-Value。

智能决策建议：根据统计学显著性，系统自动给出“推行策略”、“继续观察”或“样本量不足”的业务建议。

3. 深度下钻与辛普森悖论检测 (Deep Insight)
维度拆解 (Drill-down)：支持地域、渠道、用户分层等多维度实时切换。

悖论预警：专门针对“辛普森悖论”设计逻辑，揭示大盘平庸表现下掩盖的细分市场显著增长点（如二三线城市本地化策略的异质性表现）。

4. 通用化数据适配 (Universal Mapping)
动态字段映射：内置正则嗅探算法，支持上传任意格式的 CSV 业务日志，系统自动识别维度、分组及指标字段，实现零代码适配。

🧠 分析思维体现 (Analytical Mindset)
本项目不仅是代码的堆砌，更蕴含了深度的数据分析逻辑：

漏斗思维：不关注单一指标，而是关注用户生命周期的流转效率。

严谨统计：拒绝“拍脑袋”看平均值，坚持用显著性检验支撑结论。

异质性探索：通过多维下钻发现用户群体间的行为差异，支持针对性增长（SEO/GEO 专项优化）。

🛠️ 技术栈
Frontend: Streamlit (Modern SaaS UI with Custom CSS)

Analysis: Pandas, Scipy.stats

Visualization: Plotly Express (High-interaction charts)

Development: AI-Native Workflow (Cursor / Gemini-3-Flash)
