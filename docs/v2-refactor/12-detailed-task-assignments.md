# 时序数据标注工具 v2 细化任务列表与汇报节点

## 1. 后端架构师 (Backend Architect)
| 任务 ID | 任务名称 | 关键节点 | 交付物 |
| :--- | :--- | :--- | :--- |
| BA-01 | 路由蓝图化 (Blueprints) | Day 2 | backend/routes/* |
| BA-02 | 下采样引擎优化 (M4 Algorithm) | Day 4 | 增强型 /api/data 接口 |
| BA-03 | 标注持久化逻辑加固 | Day 5 | 兼容性数据层 |

## 2. 前端组件开发者 (Frontend Component Dev)
| 任务 ID | 任务名称 | 关键节点 | 交付物 |
| :--- | :--- | :--- | :--- |
| FCD-01 | API Service 层与请求拦截 | Day 1 | src/api/client.js |
| FCD-02 | 布局重构 (Navbar/Sidebar/Workspace) | Day 3 | src/components/layout/* |
| FCD-03 | 状态管理与 Prop 流转优化 | Day 5 | Index.vue 瘦身 (目标 <300行) |

## 3. 可视化专家 (Visualization Expert)
| 任务 ID | 任务名称 | 关键节点 | 交付物 |
| :--- | :--- | :--- | :--- |
| VE-01 | TimeSeriesChart.vue 受控封装 | Day 3 | TimeSeriesChart.vue |
| VE-02 | 框选与交互通讯重构 (Events-driven) | Day 5 | 解耦的 D3 交互逻辑 |
| VE-03 | 主图/缩略图联动与性能调优 | Day 7 | 高性能绘图引擎 |

## 4. 集成汇报节点 (Milestones)
- **M1: 协议基座 (Day 3)**: API 蓝图完成，前端布局容器就绪，图表原型可显示数据。
- **M2: 业务闭环 (Day 7)**: 标注流程全线打通，图表与表单联调完成。
- **M3: 交付验证 (Day 10)**: 性能达标，解决所有 Legacy 问题，文档更新完毕。
