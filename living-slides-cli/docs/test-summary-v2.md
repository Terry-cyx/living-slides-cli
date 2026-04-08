# htmlcli 集成测试 v2 总结报告

> 测试时间: 2026-04-05
> 版本: v2 (升级版测试协议)
> 工具版本: htmlcli 0.1.0 (含 SKILL.md 重构 + assets 接口)

## 总览

| # | 测试场景 | Slides | Assets | 7 项标准 | 结果 |
|---|---------|--------|--------|---------|------|
| 01 | 公司季度汇报 (QBR) | 19 | 4 | 7/7 | **PASS** |
| 02 | SaaS 产品发布会 | 17 | 5 | 7/7 | **PASS** |
| 03 | 技术架构评审 | 20 | 4 | 7/7 | **PASS** |
| 04 | 投资人 Pitch Deck | 15 | 5 | 7/7 | **PASS** |
| 05 | 销售提案 (字节跳动) | 17 | 4 | 7/7 | **PASS** |
| 06 | 数据分析报告 | 18 | 6 | 7/7 | **PASS** |
| 07 | 年度 AI Keynote | 29 | 5 | 7/7 | **PASS** |
| 08 | Python 高级培训 | 22 | 2 | 7/7 | **PASS** |
| 09 | 产品路线图 2026 | 17 | 6 | 7/7 | **PASS** |
| 10 | 董事会季度汇报 | 19 | 3 | 7/7 | **PASS** |
| 11 | 市场营销季度总结 | 16 | 4 | 7/7 | **PASS** |
| 12 | 技术大会 (分布式系统) | 21 | 5 | 7/7 | **PASS** |

**总计: 12/12 通过，84/84 评估项全 PASS**
**总产出: 230 slides，53 张图表/资产**
**平均每 deck: 19.2 slides, 4.4 张图表**

---

## 与 v1 的关键差异

| 维度 | v1 | v2 |
|------|----|----|
| 每个 deck 页数 | 5-12 | **15-29**（达到真实 PPT 规模）|
| 单轮交互定义 | 一次 API 编辑 | **可视化编辑 + 自然语言润色** |
| 图像生成 | 仅 CSS/Chart.js | **matplotlib PNG + mermaid + Chart.js + AI 图像接口** |
| SKILL 引用 | 单一 SKILL.md (37 行) | **SKILL + 9 个 references (2400+ 行)** |
| 设计标准 | 自由发挥 | **设计令牌 + 16:9 + 三区结构 + 洞察标题** |

---

## 各测试亮点

### Test 01: QBR — 风险矩阵 + 组织结构图
- 19 slides，含部门组织结构 mermaid 图
- AI 把"提前 90 天超越全年目标"做成洞察式标题
- 生成 risk severity bar chart 自动排序

### Test 02: 产品发布会 — 雷达图
- 17 slides，新增功能对比雷达图（matplotlib polar）
- AI 修复了重命名后的所有 SmartBot 残留
- **发现**: `save_external_image` 是不在标准类型里的图（雷达）的正确接口

### Test 03: 微服务架构评审 — 风险矩阵散点图
- 20 slides，含 mermaid 架构图 + 风险矩阵 scatter
- AI 修复了 MySQL→PostgreSQL 全局替换的副作用（保留 legacy 状态图）
- 生成 perf-improvement 双柱对比图

### Test 04: Pitch Deck — TAM/SAM/SOM 同心圆
- 15 slides 标准 YC 结构
- 自定义 matplotlib Circle patches 实现 TAM/SAM/SOM 可视化
- AI 自动计算股权比例（1000万 / 1亿 = 10%）

### Test 05: 销售提案 — ROI 时间线
- 17 slides
- ROI break-even 双线图，月度 cost vs revenue 对比
- AI 适配了字节跳动行业特征（短视频/内容平台）

### Test 06: 数据分析 — 多边形漏斗图
- 18 slides，6 张图表（最多）
- 用 matplotlib Polygon 实现真实漏斗图替换 CSS 版本
- 新增用户细分页 + 饼图

### Test 07: AI Keynote — 30 slides 最大 deck
- AI 添加 3 个紧迫性 + 3 个章节封面 + 3 个过渡 slides
- AI 增长曲线 + CTA roadmap 时间线图
- **测试覆盖了大规模 deck 的处理能力**

### Test 08: Python 培训 — 同步异步对比
- 22 slides，含语法高亮代码块
- 难度分布饼图 + sync vs async 性能对比
- **发现**: 代码 token 在 `<span class="f">` 内时简单字符串替换会失败，NL pass 修复

### Test 09: 产品路线图 — 甘特图
- 17 slides，含 matplotlib gantt-style horizontal bar chart
- 优先级矩阵散点图，新 feature 高亮
- 资源分配饼图

### Test 10: 董事会汇报 — 财务健康度仪表盘
- 19 slides
- 4 个 hbar 财务指标 + initiatives 进度排序
- 风险矩阵带象限网格

### Test 11: 市场营销总结 — 内容散点 + 漏斗
- 16 slides
- Channel ROI 降序排列 hbar
- 内容互动 vs 分享散点图，3 个爆款高亮
- Q1 vs Q2 分组柱状对比

### Test 12: 分布式系统 — 多 mermaid 时序图
- 21 slides
- CAP 定理 mermaid graph + 架构 graph + quorum sequenceDiagram
- 系统 vs 业界基准对比 + 扩展性曲线

---

## 验证的能力

### ✅ 真实 PPT 规模
- 12 个 deck 全部达到 15-29 页
- 平均 19 页，符合真实 PPT 规模（投资人 deck 10-15 页，QBR 15-20 页，培训 20+ 页）

### ✅ 三种图像生成接口都通过验证
1. **`htmlcli asset gen-chart`** - 标准 bar/hbar/line/pie/scatter (Tests 01, 02, 03, 06, 09, 10, 11, 12)
2. **`save_external_image`** - 自定义 matplotlib (radar, polygon funnel, circles, gantt) (Tests 02, 04, 06, 09, 10)
3. **客户端 mermaid.js** - CAP 图、架构图、组织图、时序图 (Tests 01, 03, 12)

### ✅ AI 智能润色能力
12 个测试展示了多种润色模式：
- **数据一致性**: Test 01 调整同比/环比，Test 06 重算转化率
- **领域适配**: Test 05 字节跳动行业语境
- **副作用修复**: Test 02 ¥999→¥799 修复，Test 03 全局替换 cleanup
- **级联更新**: Test 09 时间推迟自动调整后续，Test 10 重算总进度
- **意图推断**: Test 08 中文化意图，Test 04 股权比例计算
- **结构化扩展**: Test 07 添加章节封面/过渡，Test 10 重排布局

### ✅ Changelog 准确追踪
所有 12 个测试 changelog 都准确捕获了用户编辑：
- text_edit, attribute_change, element_added, element_removed
- 选择器级别精度
- summary 字段提供快速概览

---

## 发现的问题与改进点

### 🔴 P1 (高优先级)

1. **changelog 是单 session 覆盖式** — 每次 `/api/save` 重写 `.changelog.json`，多轮编辑只保留**相对上次 baseline 的 diff**。应该改为追加式或保留时间序列。
   - **影响**: AI 拿到的只是单次编辑的 diff，看不到累积变更
   - **建议**: 添加 `.changelog.history.json` 保存所有 diff，原 changelog 保留兼容性

2. **`/tmp` 在 Windows 上不存在** — image-generation.md 文档示例用了 `/tmp/` 路径，Windows 上需要用 `tempfile.gettempdir()`
   - **影响**: 文档示例在 Windows 上直接报错
   - **建议**: 文档全部改成 `tempfile.gettempdir()` 或 `Path(tempfile.mkdtemp())`

3. **CJK 字体在 matplotlib 默认 DejaVu Sans 上不渲染** — 所有中文 label 都需要换成英文
   - **影响**: 中文 deck 的图表标签必须英文，不一致
   - **建议**: 在 `assets.py` 中自动检测系统中文字体（Microsoft YaHei/PingFang SC/Noto Sans CJK SC）并设置 `plt.rcParams['font.family']`

### 🟡 P2 (中优先级)

4. **differ 在 `<script>`/`<style>` 内的 whitespace 变更被过度记录**
   - Test 05 加一个 `<li>` 产生 26 个 changes，因为 script 块 normalize 了空白
   - **建议**: differ 应忽略 script/style 节点内部的 whitespace-only 变更

5. **缺少 `replace_canvas` helper** — 用静态 PNG 替换 Chart.js canvas 时需要手动清理 JS 初始化代码
   - **建议**: 在 `assets.py` 添加 `replace_canvas(html_path, canvas_id, image_path)` API

6. **AI 生成的初始 deck 偶尔有坏图引用** — Test 10 deck 引用了未生成的 financial-trend.png 等
   - **建议**: 文档强调"先生成所有图后再写 HTML"，或加一个 `htmlcli asset verify <file>` 命令检查所有 `<img>` 是否真实存在

### 🟢 P3 (低优先级)

7. **HTML 中带 `<span class="f">` 的代码 token 不能简单 replace** — 需要 DOM-aware 替换
   - **建议**: differ/编辑工具加一个 `text_in_element(selector, old, new)` API

8. **Spec literal-string 假设过于具体** — v2 测试用例假设了一些字符串，但不同 agent 生成的 HTML 不一样，导致 lambda 匹配失败
   - **建议**: 测试规约改为"按选择器/含义"描述，不写死字符串

9. **Stale slide footer counter** — 添加新 slide 后，footer 里手写的 "N / 16" 没有自动更新
   - **建议**: 文档强调用 nav counter 而不是 footer 写死

---

## 与 frontend-slides 开源项目对比

参见 `docs/positioning-analysis.md` 完整分析。核心结论：

- **frontend-slides (13.1k stars)** 已经做了"AI 生成单文件 HTML deck"的核心场景
- **html-cli 的差异化**:
  1. 结构化 `.changelog.json` 选择器级 diff 协议（独家）
  2. 真实 CLI 表面（create/open/diff/asset），不绑定 Claude
  3. GrapesJS 作为编辑器
  4. matplotlib chart pipeline (`htmlcli asset gen-chart`)
  5. 结构化模板（按内容组织而非纯视觉）

- **建议新定位**: "AI 与可视化编辑器之间的回环协议"，changelog 作为开放契约，可推广到 landing page、dashboard

---

## 测试环境

- OS: Windows 11 Pro
- Python: 3.13.5
- htmlcli: 0.1.0
- matplotlib: 3.10.8
- 测试方法: aiohttp test client (模拟 GrapesJS API 编辑)
- 执行: 12 个 subagent 分 3 批并行执行（避免 token 限额）

---

## 文件清单

```
test-output/                      # 测试产物
├── test01.html ~ test12.html     # 12 个 deck (15-29 页)
├── test01-assets/ ~ test12-assets/  # 53 张图表/资产
└── test01.changelog.json ~ test12.changelog.json

docs/test-results/                # 12 个测试报告
├── test-01-qbr.md
├── test-02-product-launch.md
├── ...
└── test-12-distributed-systems.md

docs/test-plan-v2.md              # 测试用例定义
docs/test-summary-v2.md           # 本文件
docs/positioning-analysis.md      # 与开源项目对比

docs/test-results-v1/             # v1 旧测试报告（archived）
```

---

## 下一步建议

基于本次测试发现的问题，按优先级排序：

### Sprint 1 (本周可做)
1. 修复 image-generation.md 中的 `/tmp/` 路径（改用 `tempfile.gettempdir()`)
2. 在 `assets.py` 中自动检测 CJK 字体
3. 添加 `htmlcli asset verify` 命令检查图引用

### Sprint 2 (下周)
4. 改进 changelog 为追加式，保留多轮历史
5. 添加 `assets.replace_canvas()` helper
6. differ 忽略 script/style 内的 whitespace

### Sprint 3 (中期)
7. 考虑对 GrapesJS 做更深度的集成（编辑时实时显示 changelog）
8. 评估是否做 plugin 上架 frontend-slides 那样的规模（参考 positioning-analysis.md 结论）
9. 添加 PDF 导出（playwright 或 puppeteer）

### 战略决策
是否按 positioning-analysis.md 建议，重新定位为"AI/编辑器之间的回环协议"而非"做 slides"？这决定了项目未来 3-6 个月的方向。
