# v2-refactor 分支与 main 分支差异报告

> 生成日期: 2026-01-13
> 分析分支: `v2-refactor` vs `main`

## 一、 版本差异概述

| 统计项 | 数值 |
|--------|------|
| 提交数量 | 13 次 |
| 文件变更 | 44 个 |
| 新增行数 | +2,615 行 |
| 删除行数 | -3,214 行 |
| 净减少 | -599 行 (代码精炼) |

## 二、 提交历史

从 `main` 分支分叉后，`v2-refactor` 分支的提交历史（按时间正序）：

| 序号 | 提交ID | 提交信息 |
|------|--------|----------|
| 1 | `1e27b28` | chore: reorganize documentation and initialize modular backend structure |
| 2 | `ce86997` | feat(backend): modularize backend using Flask Blueprints |
| 3 | `8859ed1` | feat(frontend): implement API client and data transformation utilities |
| 4 | `54ce38d` | feat(frontend): extract layout components (FCD-02) |
| 5 | `ee383a3` | refactor(frontend): extract AppNavbar component from Index.vue |
| 6 | `94fe8ed` | refactor(frontend): finish Phase 1: layout refactoring and state management |
| 7 | `f91e154` | refactor(frontend): consolidate navbar components and finalize layout |
| 8 | `3ea6213` | refactor(frontend): complete encapsulation of D3 chart into TimeSeriesChart.vue |
| 9 | `327b7c5` | feat(backend): enhance annotation persistence with atomic writes |
| 10 | `8406d0b` | refactor(frontend): streamline Index.vue and establish state management baseline |
| 11 | `65149a5` | feat(frontend): add global keyboard shortcuts and enhance point-click interaction |
| 12 | `aaa1c6d` | refactor(frontend): secondary thinning of Index.vue and stress test preparation |
| 13 | `fc4d799` | fix(backend): 修复路由蓝图模块导入; feat(frontend): Vue驱动序列选择器 |

## 三、 架构变更详情

### 3.1 后端重构 (Backend)

#### 变更前 (main 分支)
- `app.py`: 单一巨型文件（700+ 行），包含所有 API 路由
- 路径配置硬编码在各处

#### 变更后 (v2-refactor 分支)
```
backend/
├── app.py              # 精简至 ~40 行，仅蓝图注册
├── config.py           # [新] 路径配置中心
├── auth.py             # 认证模块
└── routes/             # [新] 路由蓝图目录
    ├── __init__.py
    ├── auth_routes.py       # 登录/注销 API
    ├── data_routes.py       # 数据加载 API
    ├── annotation_routes.py # 标注 CRUD API
    └── label_routes.py      # 标签配置 API
```

**关键改进：**
- ✅ **路由蓝图化** (`BA-01`)：按功能模块拆分 API，提高可维护性
- ✅ **原子持久化** (`BA-03`)：引入 `tempfile` + `os.replace()` 原子写入，防止文件损坏
- ✅ **路径中心化**：统一 `config.py` 管理数据目录

---

### 3.2 前端重构 (Frontend)

#### 变更前 (main 分支)
- `Index.vue`: 2500+ 行的"上帝组件"
- D3 与 Vue 通过隐藏按钮 + 全局变量通讯
- API 调用分散，无统一错误处理

#### 变更后 (v2-refactor 分支)
```
frontend/src/
├── api/                    # [新] API 服务层
│   ├── client.js           # Axios 封装，Token 管理
│   └── dataService.js      # 业务 API 接口
├── utils/                  # [新] 工具函数
│   ├── dataTransform.js    # 数据格式转换
│   └── labelUtils.js       # 标签处理工具
├── store/                  # [新] 状态管理
│   └── index.js            # Vue.observable 轻量 Store
├── components/
│   ├── chart/
│   │   └── TimeSeriesChart.vue   # [新] D3 图表封装
│   └── layout/
│       ├── MainNavbar.vue        # [新] 导航栏
│       ├── LeftSidebar.vue       # [新] 左侧边栏
│       ├── RightSidebar.vue      # [新] 右侧边栏
│       ├── ChartArea.vue         # [新] 图表区域
│       ├── DirBrowserModal.vue   # [新] 目录浏览弹窗
│       └── LabelSettingsModal.vue # [新] 标签设置弹窗
└── views/
    └── Index.vue           # 精简至 557 行 (缩减 80%)
```

**关键改进：**
- ✅ **组件化** (`FCD-01/02`)：提取 10+ 子组件，职责清晰
- ✅ **状态管理** (`FCD-03`)：建立 `Vue.observable` 轻量级 Store
- ✅ **API 层抽象**：统一请求拦截、错误处理、Token 管理
- ✅ **D3 封装** (`VE-01`)：`TimeSeriesChart.vue` 实现数据驱动绘图
- ✅ **通讯升级** (`VE-02`)：Props/Events 替代隐藏按钮

---

### 3.3 文档重组

```
docs/
├── legacy/                   # [移动] 旧版文档
│   ├── 01-feature-list.md
│   ├── 04-api-reference.md
│   └── 05-label-config-guide.md
└── v2-refactor/              # [新/移动] 重构相关文档
    ├── 02-issues-list.md
    ├── 03-development-plan.md
    ├── 04-api-reference-v2.md         # [新]
    ├── 06-architecture-decision.md
    ├── 07-v2-optimization-roadmap.md  # [新]
    ├── 08-data-schema-spec.md         # [新]
    ├── 09-component-interface.md      # [新]
    ├── 11-team-roles-and-tasks.md     # [新]
    ├── 12-detailed-task-assignments.md # [新]
    └── 13-refactor-progress-report.md # [新]
```

---

## 四、 文件变更清单

### 4.1 后端变更

| 文件 | 变更类型 | 变更行数 |
|------|----------|----------|
| `backend/app.py` | 修改（精简） | -709 |
| `backend/config.py` | 新增 | +10 |
| `backend/routes/__init__.py` | 新增 | 0 |
| `backend/routes/annotation_routes.py` | 新增 | +165 |
| `backend/routes/auth_routes.py` | 新增 | +47 |
| `backend/routes/data_routes.py` | 新增 | +274 |
| `backend/routes/label_routes.py` | 新增 | +77 |
| `backend/generate_stress_test.py` | 新增 | +31 |
| `backend/perf_test.py` | 新增 | +32 |

### 4.2 前端变更

| 文件 | 变更类型 | 变更行数 |
|------|----------|----------|
| `frontend/src/views/Index.vue` | 修改（精简） | -2714 → 557 |
| `frontend/src/api/client.js` | 新增 | +47 |
| `frontend/src/api/dataService.js` | 新增 | +39 |
| `frontend/src/utils/dataTransform.js` | 修改 | +176 |
| `frontend/src/utils/labelUtils.js` | 新增 | +52 |
| `frontend/src/store/index.js` | 新增 | +44 |
| `frontend/src/components/chart/TimeSeriesChart.vue` | 新增 | +197 |
| `frontend/src/components/layout/ChartArea.vue` | 新增 | +238 |
| `frontend/src/components/layout/LeftSidebar.vue` | 新增 | +121 |
| `frontend/src/components/layout/RightSidebar.vue` | 新增 | +125 |
| `frontend/src/components/layout/MainNavbar.vue` | 新增 | +20 |
| `frontend/src/components/layout/DirBrowserModal.vue` | 新增 | +38 |
| `frontend/src/components/layout/LabelSettingsModal.vue` | 新增 | +57 |
| `frontend/src/assets/css/style.css` | 新增 | +149 |
| `frontend/src/assets/css/d3-global.css` | 新增 | +9 |
| `frontend/src/assets/js/LabelerD3.js` | 修改 | +12 |

---

## 五、 性能与测试

### 新增性能测试工具
- `backend/generate_stress_test.py`: 生成 10 万点测试数据
- `backend/perf_test.py`: 性能评估脚本

### 新增交互功能
- 全局快捷键 `Ctrl+S` 快速保存
- 单点点击切换标签
- 框选数据段实时统计

---

## 六、 已知遗留问题

> 以下问题来自 `13-refactor-progress-report.md`

1. **Undo/Redo 逻辑未闭环**：Store 预留占位符，UI 按钮和历史栈逻辑待实装
2. **CSS 边界微调**：重构后组件间可能存在细微布局偏差
3. **回归测试待完成**：极端情况（文件格式错误、Token 过期保存等）需压力测试

---

## 七、 合并建议

1. **合并前检查清单**：
   - [ ] 完成业务流程走测（加载→标注→保存→导出）
   - [ ] 多用户并发标注测试
   - [ ] 大数据量（10万点）性能验证
   - [ ] CSS 布局在不同分辨率下的视觉校对

2. **合并方式建议**：
   ```bash
   git checkout main
   git merge --no-ff v2-refactor -m "Merge v2-refactor: complete architecture refactoring"
   ```

---

*文档生成: 自动分析 `git diff main..v2-refactor --stat` 及代码结构*
