# 时序数据标注工具 v2 优化与重构路线图

## 1. 项目现状与痛点
- **上帝组件**: `Index.vue` (2500+ 行) 维护成本极高。
- **隐式通讯**: D3 与 Vue 通过隐藏按钮和全局变量通讯，逻辑脆弱。
- **性能瓶颈**: 大数据量下渲染延迟，缺乏高效的数据采样与分级加载。
- **代码重复**: API 调用散落在各处，缺乏统一的错误处理和 Token 管理。

## 2. 架构设计方案 (Proposed Architecture)

### 2.1 组件树结构
```text
App
├── Login (View)
└── Index (View)
    ├── AppNavbar (Layout)
    ├── MainLayout (Layout)
    │   ├── SidebarLeft
    │   │   ├── DataManager (FileTabs, PathSelector, FileList)
    │   │   └── LabelManager (OverallAttributes, LocalChanges)
    │   ├── ChartArea
    │   │   ├── TimeSeriesChart (D3 Wrapper)
    │   │   └── ChartToolbar (Stats, Tools)
    │   └── SidebarRight
    │       └── AnnotationWorkspace (AnnotationForm, AnnotationList)
    └── GlobalModals (DirBrowser, LabelSettings, etc.)
```

### 2.2 数据流设计
- **API 层**: 封装 Axios，支持 Promise 和统一报错。
- **Transform 层**: 负责 Backend <-> D3 <-> LocalState 的格式转换。
- **State 层**: 使用简单的 Observable 模式管理当前选中的文件状态、用户配置。

## 3. 开发阶段规划

### Phase 1: 基础设施 (Infrastructure)
- [ ] 实现 `src/api/client.js` (统一请求拦截)。
- [ ] 实现 `src/utils/dataTransform.js` (规范化数据结构)。
- [ ] 后端路由 Blueprint 拆分。

### Phase 2: 组件化重构 (Refactoring)
- [ ] 拆分侧边栏与导航栏组件。
- [ ] **核心任务**: 实现 `TimeSeriesChart.vue` 封装 D3 逻辑。
- [ ] 迁移标注表单与列表逻辑。

### Phase 3: 功能增强 (Enhancement)
- [ ] 优化大数据量下采样算法。
- [ ] 增加全局快捷键支持。
- [ ] 完善操作历史回滚 (Undo/Redo)。

## 4. 任务清单 (Task List)
| 任务 ID | 任务名称 | 优先级 |
| :--- | :--- | :--- |
| T-1 | 建立 API 服务模块 | 🔴 |
| T-2 | 编写数据转换工具函数 | 🔴 |
| T-3 | 封装 D3 图表为 Vue 受控组件 | 🔴 |
| T-4 | 拆分左侧文件管理组件 | 🟡 |
| T-5 | 拆分右侧标注工作区组件 | 🟡 |
| T-6 | 优化后端采样接口性能 | 🟢 |
