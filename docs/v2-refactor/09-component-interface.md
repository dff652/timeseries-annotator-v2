# 时序数据标注工具 v2 组件接口协议

## 1. TimeSeriesChart.vue (核心图表组件)
**功能**: 封装 D3.js，负责数据渲染与框选交互。
### Props
| 属性名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `chartData` | Array | 经过 transformForD3 处理后的点位数据 |
| `annotations` | Array | 当前文件已有的标注列表，用于在图上高亮已标区域 |
| `activeLabel` | Object | 当前用户选中的标签（含颜色），用于框选时着色 |
| `highlightSegments` | Array | 当前需要在图上特别高亮显示的段（如：点击右侧列表时定位） |

### Events
| 事件名 | 参数 | 说明 |
| :--- | :--- | :--- |
| `on-brush-end` | `(range)` | 框选结束，返回 `{startIdx, endIdx}` |
| `on-point-click` | `(point)` | 点击单个数据点，用于切换单个点的标签状态 |
| `on-zoom-change` | `(domain)` | 图表缩放范围变化（同步 Context Bar） |

---

## 2. FileList.vue (文件列表组件)
### Props
| 属性名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `files` | Array | 后端返回的文件列表对象 |
| `selectedFile` | String | 当前选中的文件名 |
| `sortBy` | String | 排序字段 (`name` 或 `annotation`) |

### Events
| 事件名 | 参数 | 说明 |
| :--- | :--- | :--- |
| `on-select` | `(file)` | 用户点击选择了一个文件 |
| `on-refresh` | - | 用户点击刷新按钮 |

---

## 3. AnnotationWorkspace.vue (右侧标注工作区)
### Props
| 属性名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `activeSegments` | Array | 当前框选的数据段 |
| `selectedLabel` | Object | 当前工作的标签 |
| `editData` | Object | 若处于编辑模式，传入旧标注数据 |

### Events
| 事件名 | 参数 | 说明 |
| :--- | :--- | :--- |
| `on-save` | `(annotation)` | 点击“添加/更新标注” |
| `on-reset` | - | 点击“重置” |
| `on-remove-segment` | `(segment)` | 从当前列表中移除某个段 |
