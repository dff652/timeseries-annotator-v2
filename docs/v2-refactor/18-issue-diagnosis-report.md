# v2-refactor 分支问题诊断报告

> 诊断日期: 2026-01-13
> 问题来源: 用户测试反馈
> 结论: **方案A修复完成**
> 最后更新: 2026-01-13 14:37

---

## 一、 问题诊断

### 问题1: 多次添加标注只显示首次结果

**根因分析**:
```javascript
// saveActiveLabel() 第439行
segments: this.activeSegments  // ❌ 使用计算属性而非实际数据
```

- `activeSegments` 是计算属性，依赖 `activeChartLabel` 和 `plottingApp.allData`
- 保存后调用 `resetCurrentAnnotation()`，重置了状态
- 第二次添加时，`activeSegments` 可能已经为空或不同

**修复方案**: 在保存时深拷贝 segments，而非使用计算属性引用

---

### 问题2: 索引定位失败

**根因分析**:
```javascript
// activeSegments() 第218行
.map(d => parseInt(d.time) || 0)  // ❌ 使用 d.time 而非 d.id
```

- 数据结构中使用 `d.id` 作为索引，但 `activeSegments` 解析的是 `d.time`
- 如果 `d.time` 是时间戳字符串，`parseInt()` 可能返回错误值
- 导致 segments 的 start/end 值错误

**修复方案**: 改用 `parseInt(d.id)` 或正确的索引字段

---

### 问题3: 清除标注不可用

**根因分析**:
- `clearAllLabels()` 方法存在，绑定到 ChartArea
- 但 RightSidebar 的事件可能未正确传递

---

### 问题4: x号删除无效

**根因分析**:
RightSidebar.vue 中:
```html
<!-- 第18行 -->
@click.stop="$emit('clear-label-from-chart', stat.text)"

<!-- 第33行 -->
@click.stop="$emit('remove-segment-by-range', seg)"
```

- 事件正确抛出，但 Index.vue 的处理方法可能有问题
- `removeSegmentByRange()` 依赖 `this.activeChartLabel`，如果为空则不生效

---

## 二、 结论与建议

### 问题严重程度评估

| 问题 | 严重程度 | 修复复杂度 |
|------|----------|------------|
| 多次标注失效 | 🔴 高 | 中 |
| 索引定位失败 | 🔴 高 | 低 |
| 清除标注不可用 | 🟡 中 | 低 |
| x号删除无效 | 🟡 中 | 中 |

### 建议方案

**方案A: 继续修复（推荐）**
- 针对性修复上述4个问题
- 预计工时: 2-3小时
- 优点: 保留已有重构成果
- 缺点: 可能还有其他隐藏问题

**方案B: 回退到 master 并部分重构**
- 保留 v2-refactor 的组件化结构设计
- 但将核心状态管理和方法从 master 移植
- 预计工时: 1天
- 优点: 更稳定
- 缺点: 需要较多工作量

---

## 三、 快速修复清单

如果选择方案A，需要修复:

1. **activeSegments 索引解析**
   ```diff
   - .map(d => parseInt(d.time) || 0)
   + .map(d => parseInt(d.id) || 0)
   ```

2. **saveActiveLabel 深拷贝**
   ```diff
   - segments: this.activeSegments
   + segments: JSON.parse(JSON.stringify(this.activeSegments))
   ```

3. **removeSegmentByRange 增强**
   - 不依赖 activeChartLabel，从 seg 参数获取 label

4. **清除标注事件链路检查**
   - 确保 clear-labels 事件正确传递

---

*诊断人员: AI Assistant*
*等待用户决策*
