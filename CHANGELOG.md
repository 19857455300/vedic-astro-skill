# 📋 Changelog

All notable changes to this project will be documented in this file.

本项目的所有重要变更都记录在此文件中。

---

## [v6.0] - 2026-06-07

> 🧮 **vedic-calculator 原生排盘引擎上线** — 六Skill架构完成

### ✨ 新增 vedic-calculator

**从零到一的原生排盘引擎。** 给出出生日期、时间、地点，直接计算完整星盘。无需安装 JHora 或任何第三方占星软件。

- **engine.py** — 主计算引擎，基于 pysweph + dashaflow + PyJHora
- **行星位置**：经度、星座、度数、Nakshatra（含 pada 和 lord）
- **Vimsottari Dasha**：9段大运 + 当前大运的9段小运
- **Chara Karakas**：8K 体系，含 DK 7K/8K 差异标注
- **分盘计算**：D9 / D10 / D4 / D5（PyJHora 引擎优先，自研公式兜底）
- **Shadbala 六力**：含9项修正的修正层（shadbala_pyjhora.py, 494行）
  - 修正 Hora Bala、Dig Bala、Paksha Bala、Tribhaga Bala 等 PyJHora 已知缺陷
- **SAV / BAV**：Ashtakavarga 吉凶值（SAV 总和恒等于 337）
- **尊贵度**：Compound Relationship（via dashaflow）
- **相位、宫主表、过运**
- **formatter.py** — 输出 structured_data.md，与 reader 格式完全兼容

#### 精度验证（3盘实测 vs JHora）

| 盘 | 行星 | Karakas | D9 | Dasha | Shadbala偏差 | Shadbala排序 |
|---|---|---|---|---|---|---|
| 祁县 | ✅ | 8/8 | 10/10 | 9/9 | 0.07 rupas | 5/7 |
| 莆田 | ✅ | 8/8 | 10/10 | 9/9 | 0.07 rupas | 7/7 |
| 泉州 | ✅ | 8/8 | 10/10 | 9/9 | 0.11 rupas | 7/7 |

### 🔧 移植性改造

- **依赖管理**：新增 requirements.txt（pysweph, dashaflow, PyJHora, pytz）
- **路径动态检测**：全部硬编码路径改为 `import jhora` → `__file__` 动态发现
- **Python 版本兼容**：删除4个文件中的 `sys.path` Python 版本过滤 hack
- **Python 3.8~3.13 全面支持**：pysweph 有 cp38~cp313 预编译 wheel

### 🔄 全系统接入

- **vedic-reader**：当 calculator 已安装时，reader 自动调用 calc 补充数据
- **vedic-core**：所有 Shadbala/SAV/BAV 引用统一走 calculator 计算
- **vedic-rectifier**：requirements.txt 同步更新
- **README**：全面重写为双语版（中/英），架构图更新为六Skill

---

## [v5.0.1] - 2026-05-24

> **社区反馈修复** — BOM修复 + Nakshatra校验 + Ayanamsa检测

### Reader
- 修复 SKILL.md UTF-8 BOM 导致 Claude Code frontmatter 解析失败
- 新增 Ayanamsa 被动提醒 + 主动检测（搜索 Lahiri/KP/Raman/Pushya）

### Rectifier
- 新增 Step 3d Nakshatra 边界校验（D9精调后检查 ±2° 边界）

---

## [v5.0] - 2026-05-22

> **执行阶段化重构** — 三阶段引擎 + 动态报告打包

### Reader
- 执行阶段化：连续 Steps 拆分为3个独立执行阶段，每阶段独立思考链
- 渐进写入：structured_data.md 分3次写入，防超长思考崩溃
- SAV铁规：只接受用户主动粘贴，不从 PDF 自行提取

### Report Builder
- 动态文件发现：3轮扫描（精确匹配→前缀分组→QA glob）
- 支持任意分段文件后缀

---

## [v4.9] - 2026-05-14

> **验前事定版** — SOP多维评估 + SAV映射铁规

- SAV→Bhava 映射公式明确化
- 验前事 SOP：候选池 A-H 多维评估 → P1/P5工具箱 → 3-5条
- 分盘提取门控(Path B)：D10/D4/D5 必须用户截屏确认
- 校验规则扩展至16条

---

## [v4.0] - 2026-05-10

> **工程化重构** — 双通道OCR + 时间精度联动

- 强制双通道 PDF 提取（文本层 + AI视觉交叉验证）
- 时间精度→分盘启用矩阵
- 校验规则 12→16条（燃烧、行星战争、Sandhi/Gandanta、盈月亏月）
- Rectifier 防过度校准规则

---

## [v3.0] - 2026-05-06

> **五Skill架构确立**

- reader / core / career / love / rectifier 五Skill上线
- 正反双审 (Double Blind Audit) 机制
- D9身份继承矩阵五维分析
- Badhaka/Maraka 审计模块

---

## [v2.x] - 2026-05-05

- Q&A规则外置 (qa_rules.md)
- HTML报告生成脚本 (report_builder.py)

---

## [v1.x] - 2026-05-04

- 初始三Skill架构（core / career / love）
- 验前事反转：AI先预测，用户确认
- 十大板块白话文总结模板
