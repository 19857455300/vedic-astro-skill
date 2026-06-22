# Vedic Astro Skills v7 咨询工作流研究报告

## 文档目的

本报告用于整理 Vedic Astro Skills v7 在真实咨询场景中的运行方式，重点回答“接到客户后应该如何收集资料、生成数据、校验时间、调用分析模块并组织交付”，不涉及具体命盘解读。

## 适用范围

本报告基于仓库中的以下资料：

- `codex/skills/vedic-reader/SKILL.md`
- `codex/skills/vedic-calculator/SKILL.md`
- `codex/skills/vedic-core/SKILL.md`
- `codex/skills/vedic-career/SKILL.md`
- `codex/skills/vedic-love/SKILL.md`
- `codex/skills/vedic-synastry/SKILL.md`
- `codex/skills/vedic-rectifier/SKILL.md`
- `codex/skills/vedic-reader/resources/data_contract.md`
- `codex/skills/vedic-reader/resources/validation_rules.md`
- `codex/skills/vedic-core/resources/qa_rules.md`
- `codex/skills/vedic-core/resources/report_rules.md`
- 仓库根目录 `README.md`

适用于基础排盘、完整命盘审计、职业咨询、感情咨询、双人合盘和出生时间校准等服务的流程设计。

## 当前结论摘要

- `vedic-reader` 是统一咨询入口，负责接待、资料识别、数据校验、时间风险判断、验前事及后续路由。
- `vedic-calculator` 是计算基座。出生日期、时间和地点完整时，应由它生成 canonical `structured_data.md`。
- `vedic-core` 是完整命盘审计主产品，消费已经验证的 `structured_data.md`，不负责重新排盘。
- `vedic-career`、`vedic-love`、`vedic-synastry` 和 `vedic-rectifier` 是专项服务模块。
- PDF、截图和文本主要用于提取出生信息及交叉验证。除同一出生时间下的有效 JHora Shadbala 外，不应覆盖 calculator 数据。
- 商业化前最需要补齐的是统一服务 SOP、客户资料模板、交付模板、隐私规则、免责声明和人工审核标准。

---

## 1. 总览

### 1.1 七个 Skill 的职责

| Skill | 实际职责 | 系统定位 |
|---|---|---|
| `vedic-reader` | 接收出生信息、PDF、截图或文本；提取资料、交叉校验、评估时间精度、执行验前事并路由后续模块 | 统一咨询入口、数据初诊台 |
| `vedic-calculator` | 根据出生日期、时间、坐标、时区计算完整星盘，生成 canonical `structured_data.md` | 计算基座、主数据生成器 |
| `vedic-core` | P1-P12 行星审计、D9 交叉分析、12 宫诊断、十大人生板块、Q&A | 完整命盘审计主产品 |
| `vedic-career` | D1/D9/D10/D4 职业分析、职业生态位、天赋格局、变现与时间窗口 | 职业专项模块 |
| `vedic-love` | 5/7 宫、Venus、PK/DK、UL、D9、Dasha 与过运分析 | 感情与恋爱时机专项 |
| `vedic-synastry` | 比较两份星盘，分析关系性质、双方承载力、方向性叠盘和时机共振 | 双人关系专项 |
| `vedic-rectifier` | 用五个重大人生事件逆推出生时间，并用新时间重算全盘 | 出生时间校准专项 |

### 1.2 架构定位

- **统一入口：** `vedic-reader`。README 明确说明用户只需说“读盘”或“占星”即可启动，由 reader 判断输入类型并路由。
- **计算基座：** `vedic-calculator`。只要出生日期、时间、地点完整，就应优先由 calculator 生成主数据。
- **核心交付：** `vedic-core`。它消费已经验证的数据，完成完整审计，不承担原始排盘职责。
- **专项咨询：** `vedic-career`、`vedic-love`、`vedic-synastry`、`vedic-rectifier`。

整体链路：

```text
客户资料
  ↓
reader 接待与路由
  ↓
calculator 生成 structured_data.md
  ↓
reader 校验、时间风险评估、验前事
  ↓
core 完整审计
  ↓
career / love / synastry / Q&A
```

来源：`README.md`、各 Skill 的 `SKILL.md`。

---

## 2. 触发条件表

| Skill | 触发关键词或场景 | 必要输入 | 产出 | 是否依赖 `structured_data.md` | 其他依赖 |
|---|---|---|---|---|---|
| reader | 读盘、星盘、印占、占星、vedic、看盘、排盘；上传 PDF 或截图 | 出生信息，或 PDF、截图、文本 | `structured_data.md`、验前事、时间可信度；可能产生 `user_context.md` | 可读取已有文件，也负责组织生成 | 优先调用 calculator；低命中时路由 rectifier |
| calculator | 直接排盘、计算星盘、不用 JHora、快速排盘、算一下 | 日期、时间、地点、lat、lon、IANA 时区；可附性别、感情状态、时间精度 | `structured_data.md` | 它是生产者 | `engine`、`transit`、`formatter` |
| core | 星盘审计、完整分析、P1-P12、开始分析、看看运势、生成报告 | 已验证的 `structured_data.md` | 身份概览、行星审计、分盘审计、宫位报告、十大板块、附录、Q&A | 强依赖 | 建议先经过 reader 验前事 |
| career | 职业分析、事业方向、10 宫分析、D9 事业、Navamsa 事业 | `structured_data.md`；最好已有 core 报告 | `career_phase12.md`、`career_phase3.md`、`career_phase4a/b/c.md` | 强依赖 | core 可选但推荐；允许快速模式 |
| love | 恋爱运势、桃花时机、感情分析、5/7 宫、PK/DK、Upapada | `structured_data.md`，含性别、感情状态、D9、Dasha | `love_step1.md`、`love_step2.md`、`love_step3.md` | 强依赖 | core 可选但推荐 |
| synastry | 合盘、匹配度、婚配、合作搭档、关系分析、配对 | 双方各一份 `structured_data.md`；关系类型和阶段可后补 | `synastry_data.md`、intake、00-04 五份关系报告 | 双份强依赖 | 缺盘时调用 calculator/reader；完整模式可引用 core |
| rectifier | 校准时间、时间矫正、出生时间不准；reader 建议校准 | 当前 `structured_data.md`、五个重大事件及日期 | `rectification_report.md`；必要时重算 `structured_data.md` | 强依赖 | calculator 重算；`time_scan.py` 扫描 |

来源：各 Skill 的 frontmatter、前置条件和输出规则。

---

## 3. 三条主流程

### 3.1 路径 A：客户只提供出生日期、时间、地点

1. reader 接收出生日期、24 小时制时间和城市。
2. 补收以下信息：
   - 性别
   - 感情状态
   - 时间精度
   - 时间来源
   - 主要咨询方向
3. 将城市转换为经纬度和 IANA 时区。
4. calculator 生成 `structured_data.md`。
5. 执行基础校验：
   - SAV 总和为 337
   - 十颗行星完整
   - Rahu/Ketu 相差 180°
   - Lagna 合理
   - 其他数学校验及分盘可信度检查
6. reader 进入 Calc 模式，不重复排盘计算。
7. 执行信号预扫、时间风险分轨和验前事。
8. 根据结果路由：
   - 时间可信度高：进入 core 或专项咨询。
   - 时间存疑：建议 rectifier。
   - 客户拒绝校时：标注中或低可信度，限制敏感分盘的使用。

来源：`vedic-reader/SKILL.md`、`vedic-calculator/SKILL.md`。

### 3.2 路径 B：客户提供 JHora PDF 或截图

1. reader 从材料中提取出生日期、时间和地点。
2. 获得完整出生信息后，必须调用 calculator 生成 canonical 数据。
3. PDF 执行双通道处理：
   - 文本层提取出生信息、行星、Dasha、SAV 和 Shadbala。
   - 视觉通道辅助识别 D1/D9，不覆盖 calculator。
4. 数据优先级：
   - 行星位置、Lagna、分盘、SAV/BAV、Dasha、宫主、尊贵度、特殊点和过运，以 calculator 为准。
   - Shadbala 先保留 calculator 基准；同一出生时间的有效 JHora PDF 可逐行覆盖展示值。
   - PDF 缺失的 Shadbala 行继续使用 calculator。
5. 出现差异时先检查：
   - 出生日期、时间和地点
   - 时区
   - Lahiri/Ayanamsa 设置
   - Mean Node/True Node
   - PDF 是否由同一出生时间生成
6. 完成交叉验证后进入 reader 验前事，再进入 core 或专项模块。

来源：`vedic-reader/SKILL.md`“数据源优先级铁规”、`data_contract.md`。

### 3.3 路径 C：出生时间不确定，需要校时

1. 先用当前估计时间生成初始 `structured_data.md`。
2. reader 根据时间来源、Lagna 边界和验前事命中率判断是否触发 rectifier。
3. rectifier 收集五个重大事件，每个至少精确到月份。
4. 将事件映射到对应宫位和 Karaka，检查其 Mahadasha/Antardasha 匹配。
5. 按原始时间精度确定扫描范围：
   - 分钟级：扫描 ±15 分钟。
   - ±15 分钟：扫描 ±30 分钟。
   - ±1 小时：扫描 ±60 分钟。
6. 先确认 Lagna 区间，再渐进校准：
   - D9：目标约 ±10 分钟。
   - D10：目标约 ±5 分钟。
   - D4/D5：可选进一步校验。
7. 如果推荐时间变化超过五分钟、Lagna 变化或 D9 Lagna 变化：
   - 必须用 calculator 重新计算全盘。
   - 重新生成 Dasha、分盘、过运和 Shadbala。
   - 旧 PDF Shadbala 失效。
   - 用新 Dasha 重新匹配事件。
8. 可做二至三条盘外盲审验证，再进入 core。

来源：`vedic-rectifier/SKILL.md`、`vedic-reader/SKILL.md`。

---

## 4. 各咨询产品对应流程

| 服务 | 推荐调用链 |
|---|---|
| 完整命盘审计 | reader → calculator → reader 验前事 → core |
| 职业方向分析 | reader → calculator → reader 验前事 → core → career |
| 感情时机分析 | reader → calculator → reader 验前事 → core → love |
| 两人合盘分析 | 双方分别 calculator/reader → 两份 `structured_data.md` → synastry 平扫 → intake → 通用或专属深析 |
| 出生时间校准 | calculator 生成初始盘 → reader 发现风险 → rectifier → calculator 重算 → reader 重验 → core |
| 快速排盘但不解读 | calculator → 基础校验 → 交付 `structured_data.md`，停止 |

补充说明：

- career 和 love 允许只基于 `structured_data.md` 运行快速模式，但商业咨询更稳妥的路径是先完成 core，因为专项模块会复用 core 的成熟审计结论。
- 合盘不应默认按恋爱关系处理。必须先做中性平扫，再由客户声明恋人、合作、朋友或家人关系。

来源：`vedic-career/SKILL.md`、`vedic-love/SKILL.md`、`vedic-synastry/SKILL.md`。

---

## 5. 客户资料收集清单

### 5.1 基础排盘

必填：

- 出生日期
- 出生时间，24 小时制
- 出生城市及国家或地区
- 时间精度
- 时间来源

建议收集：

- 性别
- 感情状态
- 是否有原始 JHora PDF
- 是否使用过其他出生时间版本

经纬度和时区应由服务方核验，不建议直接依赖普通客户自行填写的数据。

### 5.2 职业咨询

在基础排盘资料之外，收集：

- 想解决的具体问题：选行业、转岗、创业、升职或时间窗口
- 当前候选方案，用于后续 Q&A 比较
- 是否需要完整 core 审计

职业推荐的生成依据只能是盘面数据；客户经历只适合用于问题定位和最终建议，不得反向生成职业方向。

来源：`vedic-career/SKILL.md`。

### 5.3 感情咨询

在基础排盘资料之外，收集：

- 性别
- 当前感情状态
- 咨询目标：桃花、婚姻、现有关系、复合或时间窗口
- 如果询问某段具体关系，考虑升级为 synastry 并收集对方资料

既往感情经历不应成为原盘结论的生成依据。

来源：`vedic-love/SKILL.md`。

### 5.4 合盘咨询

双方分别提供：

- 出生日期
- 出生时间
- 出生地点
- 时间精度和来源
- 可选 PDF 或已有 `structured_data.md`

关系层面需要：

- 现实关系类型
- 当前阶段
- 具体问题
- 对方资料的授权和知情范围

来源：`vedic-synastry/SKILL.md`。

### 5.5 校时咨询

- 当前采用的出生时间
- 估计误差范围
- 时间来源
- 出生地点
- 五个重大事件
- 每个事件的年月，越精确越好
- 事件建议覆盖婚、丧、职、灾、财等不同领域

来源：`vedic-rectifier/SKILL.md`。

---

## 6. 交付物结构

### 6.1 `structured_data.md`

性质：内部主数据和审计底稿，不是面向客户的最终解读报告。

主要包含：

- 出生元信息
- 用户基础信息
- 行星位置
- Chara Karakas
- Nakshatra
- Shadbala
- SAV/BAV
- Dasha
- 宫主表、尊贵度、相位
- D9/D10/D4/D5
- 校验结果
- 当前过运

适合内部留档、模块间传递和技术审计，不适合直接作为普通客户的阅读交付。

### 6.2 Core 报告

规范列出的文件包括：

- `p1_overview.md`
- `p2a_planets.md` 至 `p2d_planets.md`
- `p3a_d9.md`
- `p3b_divisional.md`
- `p4a_houses.md`
- `p4b_houses.md`
- `p5a_life.md`
- `p5b_life.md`
- `appendix.md`

适合：

- 打包为 HTML
- 再转为 PDF
- 作为高客单完整咨询报告
- 作为后续私域 Q&A 的依据

不适合直接作为小红书图文，应另做脱敏摘要。

### 6.3 Career 报告

文件：

- `career_phase12.md`
- `career_phase3.md`
- `career_phase4a.md`
- `career_phase4b.md`
- `career_phase4c.md`

适合职业咨询 PDF、私域咨询纪要和行动建议清单。可进一步拆成公开内容，但应移除出生信息和确定性预测。

### 6.4 Love 报告

文件：

- `love_step1.md`
- `love_step2.md`
- `love_step3.md`

适合感情专项 PDF、桃花时间轴和私域咨询纪要。公开内容必须匿名，避免将“窗口”表达成绝对婚期。

### 6.5 Synastry 报告

合盘子目录包括：

- `intake.md`
- `structured_data_B.md`
- `synastry_data.md`
- `reports/00_signal_triage.md`
- `reports/01_individual_capacity.md`
- `reports/02_interaction_matrix.md`
- `reports/03_timing.md`
- `reports/04_guidance.md`

适合私密 PDF 和关系咨询纪要。不建议直接改为公开图文，因为涉及两个人的隐私和授权。

### 6.6 Rectifier 报告

- `rectification_report.md`
- 必要时更新后的 `structured_data.md`

适合作为完整报告的技术附录或独立校时纪要。不适合直接制作公开内容，因为推理高度个案化且包含重大人生事件。

### 6.7 当前导出能力

仓库已有 `report_builder.py` 用于生成 HTML，并支持选择 core、career 等模块。当前研究材料中未看到正式 PDF 导出或小红书图文模板。

来源：`vedic-core/resources/report_rules.md`。

---

## 7. 商业咨询风险点

### 7.1 出生时间不准

出生时间会影响 Lagna、D9、D10、D4、D5 和 Dasha 起算。项目已设计时间风险分轨和 rectifier，但不能把“客户自称精确”直接当作可靠依据。

来源：reader 时间来源修正矩阵、`vedic-rectifier/SKILL.md`。

### 7.2 地理坐标或时区错误

calculator 文档要求根据城市填写经纬度和时区，但当前研究材料中没有正式的地理编码核验流程。重名城市、历史时区和夏令时可能造成风险。

### 7.3 PDF 与 calculator 数据冲突

规则明确：除同一出生时间下的有效 JHora Shadbala 外，PDF 不得覆盖 calculator。执行商业咨询时应保留差异记录，不能凭视觉判断选值。

### 7.4 Shadbala 与 SAV 校验风险

- SAV 必须等于 337。
- BAV 行和应满足固定常量。
- Shadbala 应重视排序和强弱分级，不宜对具体小数过度解释。
- 校时后旧 PDF Shadbala 必须作废。

来源：`data_contract.md`、`validation_rules.md`。

### 7.5 AI 过度解释

项目已经设置：

- 盲审
- 禁止反向推导
- 正反双审
- 验前事不准时不得改口
- 不得把用户的痛苦直接解释成天赋

但 core 报告篇幅要求较高，仍存在为了满足篇幅而把弱信号扩写成强结论的风险，需要人工审核。

### 7.6 医疗、法律和投资边界

当前文档涉及健康、投资和婚姻时机等内容，但没有一套统一、显式的商业免责声明。现有约束包括：

- 健康只做预防提醒，不表达必然疾病。
- Maraka 只表达风险窗口，不表示必然事件。
- 不推荐宝石或仪式等迷信补救。
- 合盘不能替代对暴力、控制和财务欺骗的现实判断。

商业交付仍应明确标注：

- 非医疗诊断
- 非法律意见
- 非投资建议
- 不替代心理咨询或危机干预

### 7.7 客户期待绝对预测

文档反对单点式“某年必结婚”，更强调时间窗口和多阶段模型。但 rectifier 中存在“给出确定性结论”的措辞，容易被客户理解成科学精确度，应进一步说明方法边界。

### 7.8 隐私风险

`structured_data.md`、`user_context.md` 和合盘资料包含出生信息及人生事件。项目已有部分隔离规则，但缺少明确的数据保存期限、删除机制和双方授权记录。

---

## 8. 推荐接单 SOP

### 第一步：收集信息

使用标准表单收集：

- 服务类型
- 出生日期、时间、地点
- 时间来源和估计误差
- 性别、感情状态
- 核心问题
- 是否有 JHora PDF
- 隐私与免责声明确认

合盘额外收集双方授权、关系类型和阶段。

### 第二步：生成 structured_data

- 核验城市、经纬度和时区。
- calculator 生成 canonical `structured_data.md`。
- PDF 只用于交叉验证，Shadbala 按例外规则合并。
- 记录数据来源和版本。

### 第三步：验前事与校验

- 检查 SAV、BAV、行星完整性、Ra-Ke、Ayanamsa 和分盘可信度。
- reader 执行一次验前事。
- 记录准、不准、部分准，不允许事后改口。
- 根据时间来源、Lagna 边界和命中率决定是否校时。

### 第四步：进入 core 或专项模块

- 完整咨询：先 core。
- 职业咨询：core 后运行 career。
- 感情咨询：core 后运行 love。
- 合盘咨询：双方数据分别合格后进入 synastry。
- 时间存疑：先 rectifier，重算后再分析。

### 第五步：整理交付

建议客户版包含：

- 一页结论摘要
- 核心支持与制约信号
- 时间窗口及置信度
- 行动建议
- 风险与免责声明
- 可选技术附录

内部保留完整 Markdown 文件和 `structured_data.md`，客户交付使用 HTML 或 PDF。

### 第六步：复盘问答

- 优先引用已有报告，不重新临时推导。
- 判断性问题必须同时列出支持和制约。
- 区分“方向正确”和“执行困难”。
- 记录新的问题与答复。
- 多项偏差时，不继续硬解释，应回到出生时间和数据质量检查。

---

## 9. 后续改进建议

### 9.1 文档需要补充或统一

1. README 仍写 Python 3.8-3.13，而 calculator 已要求 Python 3.10-3.13，并推荐 Python 3.12。
2. `user_context.md` 权限规则存在冲突：
   - reader 规定仅 reader/rectifier 可读，core/career/love 禁止读取。
   - core QA 又规定回答前必须读取。
   - 需要明确最终权限模型。
3. core 文件数量描述不一致：
   - 文件结构实际列出十二个文件。
   - 完成提示称“共十一个文件”。
4. 增加一份真正面向咨询师的统一 SOP，避免从七个 Skill 中拼接流程。
5. 增加统一商业免责声明、隐私政策和客户授权模板。
6. 明确“验前事”和“校时”不是科学验证或准确率承诺。

### 9.2 值得增加的 CLI 或模板

- 城市地理编码与时区核验 CLI
- `structured_data.md` schema validator
- PDF 出生信息和 Shadbala 提取 CLI
- 一键咨询工作目录初始化工具
- 运行状态清单或 manifest
- 客户资料 intake 模板
- 客户摘要报告模板
- PDF 导出工具
- 小红书脱敏摘要模板
- 双人合盘授权记录模板
- 数据归档和删除工具

### 9.3 必须保留人工审核的环节

- 城市、坐标和时区
- 出生时间来源
- PDF 是否与当前出生时间一致
- Shadbala 差异
- 时间敏感分盘是否允许启用
- 校时事件真实性和日期精度
- 医疗、法律和投资措辞
- 合盘双方隐私和授权
- 所有“必然、注定、一定发生”类表达
- 最终客户摘要是否超出底层数据支持

---

## 下一步建议

基于本研究报告，建议继续制作以下四份独立文档：

1. `SERVICE_SOP`：定义各服务从收单、排盘、校验、分析到交付的标准流程。
2. `CLIENT_INTAKE_TEMPLATE`：统一基础排盘、职业、感情、合盘和校时的客户资料收集格式。
3. `DELIVERY_TEMPLATE`：统一客户版摘要、完整报告、时间窗口、行动建议和技术附录的交付结构。
4. `RISK_AND_DISCLAIMER`：统一隐私、数据授权、医疗、法律、投资、心理健康和预测边界声明。
