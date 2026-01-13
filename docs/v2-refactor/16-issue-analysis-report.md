# 当前版本功能问题分析报告

> 报告日期: 2026-01-13
> 分支: `v2-refactor`
> 基于用户反馈的功能测试结果
> 最后更新: 2026-01-13

---

## 一、 问题清单

| 序号 | 问题描述 | 严重程度 | 状态 |
|------|----------|----------|------|
| 1 | 标注后的CSV文件缺少标识 | 🔴 严重 | ✅ 已修复 |
| 2 | 选择标签框选不生效 | 🔴 严重 | ✅ 已修复 |
| 3 | 没有对应颜色的点显示 | 🔴 严重 | ✅ 已修复 |
| 4 | 数据段索引点击无法定位 | 🟡 中等 | ✅ 已修复 |

> **问题4修复说明**: `panChartToRange` 方法检查条件错误，对比 master 分支后修复。添加了输入验证和 toast 提示。

---

## 二、 问题详细分析

### 问题 1: 标注后的CSV文件缺少标识

#### 问题表现
导出的 CSV 文件中，标注的 label 列为空或数据格式错误。

#### 根因分析

**文件位置**: `frontend/src/assets/js/LabelerD3.js` 第 1009-1037 行

```javascript
$("#export").click(function () {
  var csvContent = plottingApp.headerStr + "\n";  // ❌ headerStr 未定义

  plottingApp.allData.forEach(function (dataArray) {
    var date = dataArray.actual_time.toISO();  // ❌ actual_time 现在是数字，不是 DateTime
    let row = dataArray.series + "," + date
      + "," + dataArray.val + "," + dataArray.label;
    csvContent += row + "\n";
  });
  // ...
});
```

**问题原因**:
1. `plottingApp.headerStr` 从未初始化，导致 CSV 文件头部为 `undefined`
2. 重构后 `actual_time` 存储的是数字索引，调用 `.toISO()` 会报错
3. 错误导致导出流程中断，文件不完整

#### 修复方案

```javascript
// 在 drawLabeler 函数初始化部分添加
plottingApp.headerStr = "series,idx,val,label";

// 修改导出逻辑
$("#export").click(function () {
  var csvContent = plottingApp.headerStr + "\n";

  plottingApp.allData.forEach(function (dataArray) {
    // 使用数字索引而非 DateTime
    var idx = dataArray.actual_time;
    let row = dataArray.series + "," + idx
      + "," + dataArray.val + "," + (dataArray.label || '');
    csvContent += row + "\n";
  });
  // ...
});
```

#### 修复位置
- 文件: `frontend/src/assets/js/LabelerD3.js`
- 行号: 初始化区域 (~第160行) 和导出函数 (~第1009行)

---

### 问题 2: 选择标签框选不生效

#### 问题表现
在左侧选择标签后，在主图上框选区域，点不会被着色为对应标签颜色。

#### 根因分析

**数据流追踪**:
```
LeftSidebar.vue (点击标签)
    ↓ @toggle-local-label
Index.vue (toggleLocalLabel 方法)
    ↓ 更新 activeChartLabel
ChartArea.vue (props: selectedLabel)
    ↓ props
TimeSeriesChart.vue (props: selectedLabel)
    ↓ watch: selectedLabel
plottingApp.selectedLabel
    ↓ 使用于 search 函数
LabelerD3.js (第729行 search 函数)
```

**关键代码** (`LabelerD3.js` 第 729-733 行):
```javascript
function search(quadtree, brush_xmin, brush_ymin, brush_xmax, brush_ymax) {
  // Skip if no label is selected - don't color points without a label
  if (!plottingApp.selectedLabel || plottingApp.selectedLabel === '') {
    return;  // ❌ 标签未传递时直接返回
  }
  // ...
}
```

**可能断点**:
1. `toggleLocalLabel` 未正确更新 `activeChartLabel`
2. `activeChartLabel` 未正确映射到 `TimeSeriesChart` 的 `selectedLabel` prop
3. `TimeSeriesChart` 的 `watch` 未触发
4. `plottingApp.selectedLabel` 更新时机晚于框选操作

#### 验证步骤

1. 在 `Index.vue` 的 `toggleLocalLabel` 方法添加日志:
```javascript
toggleLocalLabel(label, catId) {
  console.log('toggleLocalLabel called:', label, catId);
  console.log('Before - activeChartLabel:', this.activeChartLabel);
  // ... existing code
  console.log('After - activeChartLabel:', this.activeChartLabel);
}
```

2. 在 `TimeSeriesChart.vue` 的 watch 添加日志:
```javascript
selectedLabel(newVal) {
  console.log('TimeSeriesChart selectedLabel changed to:', newVal);
  // ...
}
```

3. 在 `LabelerD3.js` 的 `search` 函数添加日志:
```javascript
console.log('search called, selectedLabel:', plottingApp.selectedLabel);
```

#### 修复方案

需要确保标签选择与框选操作的同步：

**方案 A**: 检查 Index.vue 的 toggleLocalLabel 逻辑
```javascript
// 确认 activeChartLabel 被正确更新
toggleLocalLabel(label, catId) {
  // 如果点击的是已激活的标签，取消激活
  if (this.activeChartLabel === label.text) {
    this.activeChartLabel = '';
  } else {
    // 否则激活新标签
    this.activeChartLabel = label.text;
    this.activeLabelColor = label.color;  // ✅ 同时更新颜色
  }
}
```

**方案 B**: 检查 ChartArea.vue 的 props 传递
```html
<!-- 确认 selected-label prop 使用正确的数据源 -->
<time-series-chart
  :selected-label="selectedLabel"
  :label-color="labelColor"
/>
```

---

### 问题 3: 没有对应颜色的点显示

#### 问题表现
即使框选成功，点也不显示对应标签的颜色。

#### 根因分析

**关键函数** (`LabelerD3.js` 第 937-964 行):
```javascript
function getPointStyle(d) {
  if (isSelected(d)) {
    var color = null;
    
    // Priority 1: 匹配当前选中的标签，使用 labelColor
    if (plottingApp.labelColor && d.label === plottingApp.selectedLabel) {
      color = plottingApp.labelColor;
    }
    
    // Priority 2: 从 labelList 查找
    if (!color && plottingApp.labelList) {
      var labelEntry = plottingApp.labelList.find(l => l.name === d.label);
      if (labelEntry && labelEntry.color) {
        color = labelEntry.color;
      }
    }
    
    // Priority 3: 默认颜色
    if (!color) {
      color = '#7E4C64';
    }
    
    return "fill: " + color + "; stroke: " + color + "; opacity: 0.75;"
  } else {
    return "fill: black; stroke: none; opacity: 1;"
  }
}
```

**可能问题**:
1. `labelList` 未正确传递或格式不匹配
2. `labelColor` 未随标签切换更新
3. `updateSelection()` 未被调用

#### 验证步骤

1. 在 `getPointStyle` 添加日志:
```javascript
console.log('getPointStyle:', d.label, plottingApp.selectedLabel, plottingApp.labelColor);
console.log('labelList:', plottingApp.labelList);
```

2. 检查 `TimeSeriesChart.vue` 初始化时的 labelList:
```javascript
console.log('initChart - labelList:', this.labelList);
console.log('Mapped labelList:', this.plottingApp.labelList);
```

#### 修复方案

**确保 labelList 同步更新**:
```javascript
// TimeSeriesChart.vue - 添加 labelList watcher
watch: {
  labelList: {
    handler(newVal) {
      if (this.plottingApp && newVal) {
        this.plottingApp.labelList = newVal.map(l => ({ name: l.text, color: l.color }));
        this.recolor();
      }
    },
    deep: true
  }
}
```

**确保框选后调用 updateSelection**:
```javascript
// brushedMain 函数最后
search(plottingApp.quadtree, xmin, ymin, xmax, ymax);
updateSelection();  // ✅ 确保已调用
plottingApp.plot.main_brush.call(plottingApp.main_brush.move, null);
```

---

## 三、 问题关联性分析

三个问题可能存在共同根因：**Vue-D3 状态同步问题**

```
┌─────────────────────────────────────────────────────────┐
│                 Vue 组件状态                             │
│  activeChartLabel, activeLabelColor, labelList         │
└────────────────────────┬────────────────────────────────┘
                         │ Props/Events
                         ▼
┌─────────────────────────────────────────────────────────┐
│              TimeSeriesChart.vue                        │
│  维护 plottingApp 对象，通过 watch 同步状态             │
└────────────────────────┬────────────────────────────────┘
                         │ 直接操作
                         ▼
┌─────────────────────────────────────────────────────────┐
│               LabelerD3.js                              │
│  plottingApp.selectedLabel                              │
│  plottingApp.labelColor                                 │
│  plottingApp.labelList                                  │
│                                                         │
│  ❌ 这三个变量可能在需要时尚未更新                       │
└─────────────────────────────────────────────────────────┘
```

**建议统一修复方案**:

1. 在 `TimeSeriesChart.vue` 中确保所有相关属性都有 watcher
2. 在框选触发前，强制同步一次状态
3. 考虑使用 Vue 的 `$nextTick` 确保 DOM 更新后再执行 D3 操作

---

## 四、 修复优先级

| 优先级 | 问题 | 预计工时 | 建议执行顺序 |
|--------|------|----------|--------------|
| P0 | 问题2 (框选不生效) | 4h | 1 |
| P0 | 问题3 (颜色不显示) | 3h | 2 |
| P0 | 问题1 (CSV导出) | 2h | 3 |

---

## 五、 调试命令

```bash
# 启动开发服务器
cd backend && python app.py &
cd frontend && npm run dev

# 打开浏览器开发者工具 Console
# 执行以下命令检查状态
window.plottingApp.selectedLabel
window.plottingApp.labelColor
window.plottingApp.labelList
```

---

*文档作者: AI Assistant*
*基于代码静态分析和用户反馈*
