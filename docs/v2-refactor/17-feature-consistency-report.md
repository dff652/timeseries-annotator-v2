# 功能一致性检查报告

> 检查日期: 2026-01-13
> 对比分支: `main` (主分支) vs `v2-refactor` (重构分支)
> 最后更新: 2026-01-13 14:14

---

## 一、 功能清单对比

### Master 分支功能列表（共约70个方法）

#### 核心功能
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 登录/登出 | `logout()` | ✅ 存在 | ✅ |
| 加载标签配置 | `loadLabels()` | ✅ 存在 | ✅ |
| 加载当前路径 | `loadCurrentPath()` | ✅ 存在 | ✅ |
| 设置数据路径 | `setDataPath()` | ✅ 存在 | ✅ |
| 加载文件列表 | `loadFiles()` | ✅ 存在 | ✅ |
| 刷新文件列表 | `refreshFiles()` | ❌ 缺失 | � (loadFiles替代) |
| 加载结果文件 | `loadResultFile()` | ✅ 已修复 | ✅ |
| 选择文件 | `selectFile()` | ✅ 存在 | ✅ |
| 初始化图表 | `initChart()` | ✅ 存在 | ⚠️ 需检查 |
| 设置序列选择器 | `setupSelectors()` | ✅ 存在 | ⚠️ 需检查 |

#### 标签管理
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 切换局部标签 | `toggleLocalLabel()` | ✅ 存在 | ✅ |
| 检查标签选中 | `isLocalLabelSelected()` | ✅ 存在 | ✅ |
| 获取分类颜色 | `getCategoryColor()` | ✅ 存在 | ✅ |
| 获取标签颜色 | `getLabelColor()` | ✅ 存在 | ✅ |
| 添加标签 | `addLabel()` | ❌ 缺失 | 🔴 |
| 移除标签 | `removeLabel()` | ❌ 缺失 | 🔴 |
| 获取下一颜色 | `getNextColor()` | ❌ 缺失 | 🟡 |
| 根据文本查找标签 | `findLabelByText()` | ✅ 存在 | ✅ |
| 获取选中标签颜色 | `getSelectedLabelColor()` | ❌ 缺失 | 🟡 |

#### 标注工作区
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 保存当前标注 | `saveCurrentAnnotation()` | ❌ 缺失 | 🔴 |
| 重置当前标注 | `resetCurrentAnnotation()` | ✅ 存在 | ✅ |
| 选择图表标签 | `selectChartLabel()` | ✅ 存在 | ✅ |
| 保存活跃标签 | `saveActiveLabel()` | ✅ 存在 | ⚠️ 需检查 |
| 按范围删除数据段 | `removeSegmentByRange()` | ✅ 存在 | ✅ |
| 导航到数据段 | `navigateToSegment()` | ✅ 存在 | ✅ (已修复) |
| 导航到标注数据段 | `navigateToAnnotationSegment()` | ✅ 存在 | ✅ (已修复) |
| 循环标注数据段 | `cycleAnnotationSegments()` | ✅ 已修复 | ✅ |
| 平移图表到范围 | `panChartToRange()` | ✅ 存在 | ✅ (已修复) |
| 导航到标签点 | `navigateToLabelPoints()` | ✅ 已修复 | ✅ |
| 清除图表标签 | `clearLabelFromChart()` | ✅ 存在 | ✅ |
| 清除当前标签 | `clearCurrentLabel()` | ❌ 缺失 | 🟡 |
| 删除数据段 | `removeSegment()` | ❌ 缺失 | 🟡 |

#### 标注保存与导出
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 删除标注 | `deleteAnnotation()` | ✅ 存在 | ✅ |
| 编辑标注 | `editAnnotation()` | ✅ 存在 | ✅ |
| 获取认证头 | `getAuthHeaders()` | ❌ 缺失 | 🟡 (API层处理) |
| 加载文件标注 | `loadAnnotationsForFile()` | ✅ 存在 | ✅ |
| 保存标注到服务器 | `saveAnnotationsToServer()` | ✅ 存在 | ✅ |
| 下载标注 | `downloadAnnotations()` | ✅ 已修复 | ✅ |

#### 图表交互
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 清除所有标注 | `clearAllLabels()` | ✅ 存在 | ✅ |
| 更新悬停信息 | `updateHoverinfo()` | ✅ 存在 | ✅ |
| 重置图表视图 | `resetChartView()` | ✅ 存在 | ✅ |
| 触发重绘 | `triggerReplot()` | ❌ 缺失 | 🟡 |
| 触发重着色 | `triggerRecolor()` | ❌ 缺失 | 🟡 |
| 清除序列 | `clearSeries()` | ✅ 存在 | ✅ |
| 更新选择范围 | `updateSelectionRange()` | ❌ 缺失 | 🔴 |

#### 目录浏览
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 打开目录浏览器 | `openDirBrowser()` | ❌ 缺失 | 🟡 (组件化) |
| 加载目录 | `loadDirectory()` | ✅ 存在 | ✅ |
| 返回上级目录 | `goToParentDir()` | ✅ 存在 | ✅ |
| 选择当前目录 | `selectCurrentDir()` | ✅ 存在 | ✅ |

#### 标签设置管理
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 添加分类 | `addCategory()` | ✅ 存在 | ✅ |
| 删除分类 | `deleteCategory()` | ✅ 存在 | ✅ |
| 添加标签到分类 | `addLabelToCategory()` | ✅ 存在 | ✅ |
| 从分类删除标签 | `deleteLabelFromCategory()` | ✅ 存在 | ✅ |
| 生成唯一颜色 | `generateUniqueColor()` | ✅ 存在 | ✅ |
| 保存标签到服务器 | `saveLabelsToServer()` | ✅ 存在 | ✅ |
| 更新分类颜色 | `updateCategoryColors()` | ✅ 存在 | ✅ |

#### 工具方法
| 功能 | 方法名 | v2-refactor | 状态 |
|------|--------|-------------|------|
| 自然排序 | `naturalSort()` | ❌ 缺失 | 🟡 (内联) |
| 文件排序 | `sortFiles()` | ✅ 存在 | ✅ |
| 格式化数字 | `formatNumber()` | ✅ 存在 | ✅ |
| 显示提示 | `showToast()` | ✅ 存在 | ✅ |
| 加载数据 | `loadData()` | ❌ 缺失 | 🟡 (selectFile内部) |

---

## 二、 严重问题修复记录

### ✅ 问题1: `downloadAnnotations()` - 已修复
已实现完整的JSON导出逻辑，包含文件名、整体属性、标注列表和导出时间。

### ✅ 问题2: `cycleAnnotationSegments()` - 已修复
已实现点击标签循环显示各数据段的功能，包含toast提示和图表平移。

### ✅ 问题3: `loadResultFile()` - 已修复
已实现加载JSON结果文件预览标注的功能，自动加载对应的CSV文件并显示标注。

### � 问题4: `updateSelectionRange()` - 低优先级
v2-refactor 通过 `onSelectionUpdate()` 事件处理器实现了类似功能，不影响主要工作流。

---

## 三、 中等问题（已处理）

- `refreshFiles()` - 可通过 loadFiles() 替代 ✅
- `addLabel()`, `removeLabel()` - 已通过标签设置模态框替代 ✅
- `navigateToLabelPoints()` - ✅ 已修复

---

## 四、 轻微问题（影响较小）

- `getNextColor()`, `getSelectedLabelColor()` - 颜色辅助方法
- `triggerReplot()`, `triggerRecolor()` - D3触发器（组件化后可能不需要）
- `naturalSort()` - 已内联到 sortFiles()

---

## 五、 修复优先级

| 优先级 | 问题 | 影响 | 状态 |
|--------|------|------|------|
| P0 | `downloadAnnotations()` | 无法导出标注结果 | ✅ 已修复 |
| P0 | `cycleAnnotationSegments()` | 无法循环定位数据段 | ✅ 已修复 |
| P1 | `loadResultFile()` | 无法预览已有标注 | ✅ 已修复 |
| P1 | `updateSelectionRange()` | 框选信息同步 | 🟡 低优先级 |
| P2 | 其他缺失方法 | 功能不完整 | - |

---

*文档生成时间: 2026-01-13*
