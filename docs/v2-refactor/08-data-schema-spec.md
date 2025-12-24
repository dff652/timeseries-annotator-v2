# 时序数据标注工具 v2 数据格式规范协议

## 1. 原始序列数据 (Backend API -> Frontend)
**接口**: `GET /api/data/{filename}`
**数据结构**:
```json
{
  "success": true,
  "filename": "dataset.csv",
  "columns": ["timestamp", "value"],
  "data": [
    {
      "time": "2025-01-01T00:00:00", 
      "val": 12.5, 
      "series": "value", 
      "label": ""
    }
  ],
  "seriesList": ["value"],
  "labelList": []
}
```
**规范要求**:
- `time`: 必须是 ISO 8601 格式字符串。
- `val`: 必须是浮点数，无效值需转为 `null` 或 `0`。
- `series`: 序列标识符，默认为 `value`。

## 2. 标注数据结构 (Persistence & Export)
**文件位置**: `backend/annotations/{user}/{filename}.json`
**数据结构**:
```json
{
  "filename": "dataset.csv",
  "export_time": "2025-12-24T10:00:00",
  "annotations": [
    {
      "id": "ann_1735000000",
      "label": {
        "id": "upward_spike",
        "text": "上行尖峰",
        "color": "#ef4444"
      },
      "segments": [
        { "start": 100, "end": 150, "count": 51 }
      ],
      "overall_attributes": {
        "trend": "increase",
        "noise": "low"
      },
      "prompt": "问题描述文本",
      "expertOutput": "专家分析结论"
    }
  ]
}
```

## 3. 标签配置结构 (config/labels.json)
**数据结构**:
```json
{
  "overall_attribute": {
    "categories": {
      "trend": {
        "name": "趋势",
        "labels": [{"id": "up", "text": "上升"}]
      }
    }
  },
  "local_change": {
    "categories": {
      "spike": {
        "name": "尖峰",
        "labels": [{"id": "up_spike", "text": "上行", "color": "#ff0000"}]
      }
    }
  }
}
```
