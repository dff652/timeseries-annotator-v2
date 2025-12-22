# Changelog - 时序标注工具 V2

## [0.3.1] - 2025-12-22

### 🎨 UI/UX 改进

#### 框选统计优化
- **位置调整** - 将框选统计从图表右上角叠加层移至工具栏显示，避免遮挡图表
- **两行布局** - 第一行显示索引和点数，第二行显示范围、均值、标准差
- **样式优化** - 添加浅紫色背景区分，数值使用等宽字体

#### 右侧面板改进
- **标注数据段导航** - 点击已保存标注的标签可循环定位到各数据段
- **单个数据段导航** - 点击数据段 badge 可直接定位到该段
- **图上标签导航** - 点击图上标签可定位到该标签的标注点

#### 交互增强
- **图表悬停信息** - 主图点悬停显示时间、数值、标签信息
- **缩略图高度增加** - 从50px增加到80px，便于选择操作
- **防止误触右键菜单** - 缩略图区域禁用浏览器右键菜单

### 🐛 Bug修复

#### 缩略图残留问题
- **图上标签取消后缩略图残留** - 修复 `clearLabelFromChart` 方法，同时更新主图和 context (缩略图) 点的样式
- **已框选数据段取消后残留** - 修复 `removeSegment` 方法，删除段时同步清除对应数据点的标签，并更新主图和缩略图显示

#### 响应式修复
- **框选统计显示** - 修复 `selectionStats` 计算属性响应式更新问题
- **数据段列表显示** - 修复 `currentAnnotation.segments` 响应式更新问题
- **图表版本追踪** - 新增 `chartDataVersion` 和 `annotationVersion` 强制响应式更新

### 📁 文件改动

#### Frontend
- `src/views/Index.vue`
  - 重构 `clearLabelFromChart()` 同时更新主图和缩略图
  - 重构 `removeSegment()` 添加点标签清除逻辑
  - 新增 `navigateToLabelPoints()` 定位图上标签
  - 新增 `navigateToSegment()` 定位数据段
  - 新增 `navigateToAnnotationSegment()` 定位已保存标注的数据段
  - 新增 `cycleAnnotationSegments()` 循环定位标注数据段
  - 新增 `panChartToRange()` 视图平移方法
  - 框选统计移至工具栏，使用 `.selection-stats-inline` 样式
  - 删除 `.chart-with-stats` 和 `.selection-stats-chart` 旧样式

- `src/assets/js/LabelerD3.js`
  - `context_height` 从50增加到80
  - 添加缩略图右键菜单禁用
  - 新增悬停信息显示逻辑

---


## [0.3.0] - 2025-12-22

### 🔧 标注流程重构

#### 核心功能修复
- **标签管理CRUD修复** - 修复编辑分类无法保存的问题，使用直接对象引用替代计算属性副本
- **清除标注逻辑优化** - 清除图上所有点颜色，联动清除已选标签，但不清除已保存的标注列表
- **取消标签联动** - 取消已选标签时，联动清除图上该标签对应的数据点颜色
- **子标签颜色唯一** - 新增 `generateUniqueColor()` 方法，使用20色调色板自动分配不重复颜色
- **编辑标注支持** - 点击已保存标注的✏️按钮可加载到编辑区进行修改

#### 数据结构
- **一标签多段** - 一个标注 = 1个标签 + N个数据段 + 1个问题 + 1个专家分析
- **导出格式适配** - JSON导出格式支持新的一对多数据结构

### 🎨 UI/UX 改进

#### 布局修复
- **序列选择器始终可见** - 不再隐藏单序列文件的「主序列/参考序列」下拉框
- **移除重复导出按钮** - 工具栏只保留「清除标注」，右侧边栏保留「下载」按钮
- **编辑状态高亮** - 正在编辑的标注项显示紫色边框和浅紫色背景
- **动态按钮文案** - 编辑模式时保存按钮显示「更新标注」

#### 交互改进
- **标签选中视觉反馈** - 点击局部变化标签时有明确的高亮效果
- **操作反馈完善** - 添加/删除分类和标签时显示Toast提示

### 📁 文件改动

#### Frontend
- `src/views/Index.vue`
  - 新增 `editingAnnotationIndex` 状态管理编辑模式
  - 新增 `editAnnotation(idx)` 方法加载标注进行编辑
  - 新增 `usedColors` 计算属性收集已使用颜色
  - 新增 `generateUniqueColor()` 方法生成唯一颜色
  - 修复 `clearCurrentLabel()` 联动清除图上点
  - 修复 `clearAllLabels()` 不清除已保存列表
  - 修复 `saveCurrentAnnotation()` 支持更新模式
  - 修复 `addLabelToCategory()` 使用正确的对象引用
  - 修复 `deleteLabelFromCategory()` 使用正确的对象引用
  - 新增编辑状态CSS样式 `.annotation-item.editing`

### 🐛 Bug修复

- **修复框选无法添加数据段问题** - 在 `updateSelectionRange` 中强制Vue响应式更新，使用对象展开运算符更新 `currentAnnotation`
- **添加调试日志** - 在 `updateSelectionRange` 中添加console.log帮助诊断问题

### 🐛 已知待修复问题

- [ ] 标签管理弹窗分类显示问题待进一步验证
- [ ] 缩略图光标易触发浏览器右键菜单
- [ ] 工具栏位置调整（减少图表与工具栏间空白）
- [ ] 主图和缩略图尺寸优化

---

## [0.2.0] - 2025-12-21

### 🎯 核心功能修复

#### 图表渲染
- **修复图表不显示问题** - 重写了数据初始化流程，确保 D3 在 DOM 就绪后渲染
- **修复 NaN 序列化问题** - 后端将所有 NaN 值转换为 `null` 或空字符串，确保 JSON 有效性
- **修复时间格式问题** - 后端统一将时间转换为 ISO 格式（`YYYY-MM-DDTHH:mm:ss.000Z`），支持多种输入格式
- **优化 LabelerD3 初始化** - 修复 selectedSeries/refSeries 从空 DOM 获取的问题，优先使用预设值
- **增强数据验证** - 在 `updateBrushData` 中添加空数据检查和 try-catch 错误处理

#### 后端改进
- **智能列检测** - 支持中文列名（时间、日期、值、序列、标签）
- **多序列支持** - 正确识别和处理多个数据序列
- **索引作为 X 轴** - 无时间列时自动使用行索引
- **时间格式转换** - 支持多种时间格式自动转换为 ISO 标准格式

### 🎨 UI/UX 优化

#### 布局调整
- **Navbar 简化** - 移除右上角操作按钮，添加当前文件名显示
- **数据管理重新设计** - 合并"数据路径"和"数据文件"为一个卡片，添加标签页：
  - 📄 **原始数据** (CSV 文件)
  - 📝 **标注结果** (JSON 文件，支持回看和修改)
- **工具栏重新布局** - 将"清除标注"和"导出"按钮移至图表下方工具栏，与操作提示、序列选择器对齐

#### 交互改进
- **局部标签单选** - 局部变化标签改为单选模式，避免标注冲突
- **颜色一致性** - 统一使用大类颜色：
  - 左侧标签、图表标注点、已选标签区域使用相同颜色
  - 每个大类（异常突变、渐变趋势等）分配一个固定颜色
- **紧凑布局** - 左侧边栏使用卡片样式，模块边框清晰，间距优化

### 🌐 网络配置

#### 远程访问支持
- **配置服务器 IP** - 前端 API_BASE 改为 `http://192.168.199.126:5000/api`
- **数据目录设置** - 支持设置自定义数据目录（`/home/douff/数据标注/data/标注数据`）
- **跨机器访问** - 支持从 PC (192.168.199.242) 访问服务器 (192.168.199.126)

### 📁 文件改动

#### Backend
- `app.py`
  - 重写 `get_data()` 函数，增强 NaN 处理和列检测
  - 添加 `to_iso_time()` 辅助函数，统一时间格式转换
  - 支持多种时间格式：`YYYY-MM-DD HH:MM:SS`、`YYYY/MM/DD HH:MM:SS`、ISO 格式等

#### Frontend
- `src/views/Index.vue`
  - 重构 Navbar 模板（移除操作按钮）
  - 重构数据管理区域（添加 CSV/JSON 标签页）
  - 重构工具栏布局（添加操作按钮）
  - 修改 `toggleLocalLabel()` 为单选逻辑
  - 添加 `csvFiles` 和 `jsonFiles` 计算属性
  - 添加 `loadResultFile()` 方法（TODO：实现 JSON 加载逻辑）
  - 添加工具栏、标签页相关 CSS 样式
  - 添加更多大类颜色配置

- `src/assets/js/LabelerD3.js`
  - 修复 `selectedSeries`/`refSeries` 初始化逻辑
  - 添加调试日志输出
  - 增强 `updateBrushData()` 数据验证

### 🐛 已知问题

- [ ] JSON 结果文件加载功能待实现（`loadResultFile()` 方法为占位符）
- [ ] 多序列切换功能待完善
- [ ] 工具栏按钮位置需进一步调整（用户反馈太靠下）

### 📊 测试数据

- 成功加载 100 个 CSV 文件（`/home/douff/数据标注/data/标注数据`）
- 验证数据格式：date, category, value
- 验证数据量：5000 条记录

---

## [0.1.8] - 2025-12-21 晚上

### 🔧 架构重构

#### 单页应用改造
- **删除独立路由** - 移除 Labeler、Help、License 独立页面
- **功能统一到 Index** - 将标注功能直接集成到 Index.vue 主页面
- **简化路由配置** - 单一路由 `/`，避免状态丢失和数据传递问题
- **集成文件和标签管理** - 左侧面板直接显示文件列表和标签管理

#### 数据转换优化
- **新增 dataTransform.js** - 创建统一的数据转换工具函数
- **修复时间格式问题** - 保持 ISO 字符串格式传递给 D3，由 D3 内部转换
- **规范化数据结构** - 统一 API 返回数据到 D3 所需格式的转换流程

#### 代码改动
**Frontend**:
- `router/index.js` - 删除 labeler/help/license 路由（-19 行）
- `utils/dataTransform.js` - 新增数据转换工具（+130 行）
- `views/Index.vue` - 大幅重构，集成标注功能（+637/-756 行）
- `views/Labeler.vue` - 保留但不再作为独立路由使用
- `components/BaseNavbar.vue` - 简化导航栏（-5 行）

**Backend**:
- `app.py` - 优化 API 响应格式（+133 行）

---

## [0.1.5] - 2025-12-21 下午

### 📚 文档完善

#### 新增文档
- **README.md** - 项目说明、快速开始指南
- **01-feature-list.md** - 功能清单对比（V1 vs TRAINSET vs V2）
- **02-issues-list.md** - 详细的问题清单和根因分析
  - P0 问题：Labeler 页面崩溃、标签管理为空
  - P1 问题：目录浏览缺失、布局不合理
  - P2 问题：品牌和主题问题
- **03-development-plan.md** - 开发方案和阶段划分
- **04-api-reference.md** - 完整的 API 文档
- **05-label-config-guide.md** - 标签配置说明
- **06-architecture-decision.md** - 架构决策文档（SPA vs MPA）

#### D3.js LabelerD3 优化
- **代码格式化** - 516 行代码重新格式化
- **注释优化** - 添加关键函数注释
- **变量命名优化** - 提升可读性（-258/+258 行）

#### Frontend 配置
- **添加 .npmrc** - NPM 配置文件

---

## [0.1.0] - 2025-12-21 下午 (初始版本)

### 🎉 项目初始化

#### 项目集成
- **TRAINSET 前端集成** - 移植 TRAINSET 的 Vue 2.x 前端代码
- **Flask 后端集成** - 集成 timeseries-annotator-v1 的 Flask API
- **D3.js 图表** - 集成 TRAINSET 的 D3.js 时序图表渲染

#### 核心功能（继承自 TRAINSET）
- **文件上传和管理** - CSV 文件上传和服务器文件列表
- **标签配置** - `labels.json` 配置文件支持
  - 整体属性标签（Overall Attribute）
  - 局部变化标签（Local Change）
- **D3 交互式图表**
  - 时间序列可视化
  - Context Bar 导航
  - 点击/拖拽标注
- **标注导出** - JSON 格式导出

#### 项目结构
```
timeseries-annotator-v2/
├── backend/
│   ├── app.py              # Flask API 服务器
│   ├── config/
│   │   └── labels.json     # 标签配置
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Index.vue     # 主页
│   │   │   ├── Labeler.vue   # 标注页面
│   │   │   ├── Help.vue      # 帮助页面
│   │   │   └── License.vue   # 许可证页面
│   │   ├── components/
│   │   │   ├── BaseNavbar.vue
│   │   │   ├── BaseView.vue
│   │   │   ├── LabelerModal.vue
│   │   │   └── LabelerInstruction.vue
│   │   ├── assets/js/
│   │   │   └── LabelerD3.js  # D3 图表核心
│   │   ├── mixins/
│   │   │   └── LabelerColor.js
│   │   └── router/index.js
│   ├── build/              # Webpack 配置
│   ├── static/             # 静态资源
│   │   ├── files/          # 示例 CSV 文件
│   │   └── trainset_logo.png
│   └── package.json
└── .gitignore
```

#### 技术栈
- **Frontend**: Vue.js 2.x + Webpack + D3.js
- **Backend**: Flask + Python
- **数据存储**: JSON 文件

#### 示例数据
- `colorlist.csv` - 颜色列表示例
- `sample_trainset.csv` - TRAINSET 示例数据集


