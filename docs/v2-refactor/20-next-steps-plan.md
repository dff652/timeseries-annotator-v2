# v2-refactor 重构推进计划

> 日期: 2026-01-13
> 分支: v2-refactor
> 上次更新: 方案B修复成功后

---

## 一、当前状态

### 已完成
- ✅ 布局组件化拆分（MainNavbar、LeftSidebar、RightSidebar、ChartArea）
- ✅ D3 图表封装为 TimeSeriesChart.vue 组件
- ✅ API 客户端和数据转换工具抽取
- ✅ 后端路由模块化（Flask Blueprints）
- ✅ 核心功能修复（方案B）

### 代码统计

| 文件 | master | v2-refactor | 变化 |
|------|--------|-------------|------|
| Index.vue | 2561 行 | 807 行 | -68% |
| 组件总数 | 1 | 7 | +6 |
| 后端路由 | 1 文件 | 4 文件 | 模块化 |

---

## 二、已知问题

根据 [17-feature-consistency-report.md](17-feature-consistency-report.md)，以下方法仍缺失或需检查：

| 优先级 | 方法 | 状态 | 建议 |
|--------|------|------|------|
| P1 | `refreshFiles()` | 缺失 | 可用 `loadFiles()` 替代 |
| P2 | `addLabel()`, `removeLabel()` | 缺失 | 通过标签设置模态框替代 |
| P2 | `triggerReplot()`, `triggerRecolor()` | 缺失 | 评估是否需要 |
| P3 | `getNextColor()`, `getSelectedLabelColor()` | 缺失 | 低优先级 |

---

## 三、下一步计划

### 阶段1：稳定性验证（1天）

- [ ] 完整功能回归测试
  - 文件加载和切换
  - 标注、保存、导出流程
  - 标签管理
- [ ] 修复发现的任何剩余问题
- [ ] 提交代码并合并到 main

### 阶段2：状态管理优化（2-3天）

- [ ] 引入 Vuex 或 Pinia 集中管理状态
  - `plottingApp` 状态 → store
  - 减少组件间 props/events 传递
- [ ] 消除 `window.plottingApp` 全局变量依赖
- [ ] 添加 TypeScript 类型定义（可选）

### 阶段3：D3 进一步封装（2天）

- [ ] 将 LabelerD3.js 逻辑迁移到 TimeSeriesChart.vue
- [ ] 使用 Vue 响应式替代 jQuery
- [ ] 添加单元测试

### 阶段4：UI/UX 优化（持续）

- [ ] 移动端适配
- [ ] 暗色模式
- [ ] 性能优化（大数据集）

---

## 四、建议的分支策略

```
main (稳定版)
  └── v2-refactor (当前修复后)
        ├── feature/vuex-store (阶段2)
        └── feature/d3-migration (阶段3)
```

---

## 五、重构风险分析

### 为什么方案A失败而方案B成功？

| 因素 | 方案A（失败） | 方案B（成功） |
|------|---------------|---------------|
| **问题识别** | 只看到表面逻辑错误 | 识别到变量作用域根因 |
| **修复范围** | 逐个修复单点问题 | 系统性批量替换 |
| **变量引用** | 混用 plottingApp | 统一 window.plottingApp |

### 继续重构会不会重蹈覆辙？

**关键在于如何重构。** 避免方案A问题的原则：

| 原则 | 做法 | 反例 |
|------|------|------|
| **测试先行** | 每次修改前有测试覆盖 | 修改后才测试 |
| **小步提交** | 每个功能点单独提交 | 多个修改混合 |
| **统一规范** | 明确变量命名规则 | 混用引用方式 |
| **渐进替换** | 保留旧实现作为兼容层 | 直接删除/简化 |

### 安全重构路径

```
阶段2（低风险）：引入 Vuex/Pinia
       ↓
       保留 window.plottingApp 作为兼容层
       ↓
阶段3（低风险）：添加 TypeScript
       ↓
       类型定义能在编译时发现引用问题
       ↓
阶段4（中风险）：D3 逻辑迁移
       ↓
       新老代码并存，逐步切换
       ↓
阶段5（高风险）：移除 jQuery
       ↓
       只在所有功能稳定后进行
```

### 兼容层模式示例

```javascript
// 安全的迁移方式
const store = useAnnotationStore();

// 保留旧接口作为兼容层
window.plottingApp = {
  get allData() { return store.allData; },
  get selectedLabel() { return store.selectedLabel; },
  // ... 其他属性
};
```

### 建议

| 场景 | 建议 |
|------|------|
| 只需维护和小改 | **保持现状，不重构** |
| 计划添加新功能 | 在新功能开发时局部重构 |
| 有充足时间和测试 | 按阶段渐进式重构 |

---

## 六、立即行动

### 1. 提交当前修复

```bash
cd /home/dff652/TS-anomaly-detection/timeseries-annotator-v2
git add -A
git commit -m "fix: 方案B修复 - 移植master核心方法，统一plottingApp引用

修复问题：
- 清除标注功能
- 标签追加错误
- 索引段定位
- 导出功能

修改内容：
- 从master移植clearLabelFromChart、panChartToRange完整实现
- 统一所有plottingApp引用为window.plottingApp
- 增强D3刷新逻辑（主图+缩略图）

Refs: docs/v2-refactor/19-fix-report.md"
```

### 2. 可选：合并到 main

如果功能验证通过：
```bash
git checkout main
git merge v2-refactor
git push origin main
```

---

*文档创建时间: 2026-01-13 17:35*
