# 时序数据标注工具 v2

> 基于 D3.js 的时序数据可视化标注工具，支持多标签、多数据段标注

## 项目状态

🟢 **当前版本**: v0.3.1 (2025-12-23)

## 功能特性

### 📊 数据可视化
- **双视图**：主图 + 缩略图（全局导航）
- **框选统计**：实时显示索引、点数、范围、均值、标准差
- **悬停信息**：显示时间、数值、标签信息

### 🏷️ 标签管理
- **分层标签**：整体属性 + 局部变化两类标签
- **自定义颜色**：每个标签独立颜色
- **标签管理**：支持新增、编辑、删除分类和标签

### ✏️ 标注工作区
- **多标签同显**：图上所有标签一目了然
- **点击切换**：点击标签查看对应数据段索引
- **自动切换**：主图框选时自动显示当前标签的段
- **颜色一致**：数据段索引与标签颜色统一

### 💾 标注导出
- **JSON格式**：包含标签、数据段、问题、专家分析
- **一标签多段**：一个标注可包含多个数据段

## 快速开始

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端将在 http://localhost:5000 启动

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:3003 启动

## 使用流程

```
1. 左侧选择文件 → 加载时序数据
2. 左侧选择标签 → 确定标注类型
3. 主图框选区域 → 自动着色并添加到工作区
4. 填写问题/分析 → 保存标注
5. 下载导出 → 获取JSON标注文件
```

## 目录结构

```
timeseries-annotator-v2/
├── backend/              # Flask后端
│   ├── app.py           # API入口
│   ├── config/          # 配置文件
│   └── annotations/     # 标注存储
├── frontend/            # Vue.js前端
│   ├── src/
│   │   ├── views/       # Index.vue 主页面
│   │   └── assets/js/   # LabelerD3.js 图表逻辑
│   └── package.json
├── CHANGELOG.md         # 版本更新日志
└── docs/                # 文档目录
```

## 技术栈

- **前端**: Vue.js 2.x, D3.js
- **后端**: Flask, Pandas
- **存储**: JSON文件

## 更新日志

见 [CHANGELOG.md](./CHANGELOG.md)

## License

MIT
