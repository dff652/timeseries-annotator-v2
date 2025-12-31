# 时序数据标注工具 v2 API 参考手册 (重构版)

## 基础信息
- **Base URL**: `/api`
- **认证**: JWT Token (Bearer 模式)

## 1. 认证模块 (Auth Blueprint)
- `POST /api/login`: 登录获取 Token。
- `GET /api/user`: 获取当前用户信息。

## 2. 数据模块 (Data Blueprint)
- `GET /api/files`: 获取数据文件列表 (支持 path 参数)。
- `GET /api/data/<filename>`: 获取时序数据。
    - **参数**: `limit` (下采样点数，默认 10000)。
- `GET /api/browse-dir`: 浏览服务器目录结构。
- `POST /api/set-path`: 设置当前用户的数据根目录。

## 3. 标注模块 (Annotation Blueprint)
- `GET /api/annotations/<filename>`: 获取指定文件的标注列表。
- `POST /api/annotations/<filename>`: 保存标注数据 (支持原子写入)。
- `DELETE /api/annotations/<filename>`: 删除特定标注项。
- `GET /api/download-annotations/<filename>`: 导出标准格式 JSON。

## 4. 标签模块 (Label Blueprint)
- `GET /api/labels`: 获取全局标签配置。
- `POST /api/labels`: 更新标签配置。
- `POST /api/labels/custom`: 添加自定义标签。
