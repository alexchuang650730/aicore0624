# SmartUI 备份记录

## 备份信息
- 备份时间: Sun Jun 29 08:10:58 EDT 2025
- 备份目录: backup/smartui_backup_20250629_081039
- 原始路径: powerautomation_web/smartui
- 备份原因: AG-UI协议重构前的安全备份

## 备份内容验证
total 232
drwxrwxr-x 4 ubuntu ubuntu   4096 Jun 29 08:10 .
drwxrwxr-x 3 ubuntu ubuntu   4096 Jun 29 08:10 ..
-rw-rw-r-- 1 ubuntu ubuntu    221 Jun 29 08:10 .env.production
-rw-rw-r-- 1 ubuntu ubuntu    527 Jun 29 08:10 Dockerfile
-rw-rw-r-- 1 ubuntu ubuntu    424 Jun 29 08:10 components.json
-rw-rw-r-- 1 ubuntu ubuntu    844 Jun 29 08:10 eslint.config.js
-rw-rw-r-- 1 ubuntu ubuntu    390 Jun 29 08:10 index.html
-rw-rw-r-- 1 ubuntu ubuntu     95 Jun 29 08:10 jsconfig.json
-rw-rw-r-- 1 ubuntu ubuntu   2151 Jun 29 08:10 nginx.conf
-rw-rw-r-- 1 ubuntu ubuntu   2582 Jun 29 08:10 package.json
-rw-rw-r-- 1 ubuntu ubuntu 182534 Jun 29 08:10 pnpm-lock.yaml
drwxrwxr-x 2 ubuntu ubuntu   4096 Jun 29 08:10 public
drwxrwxr-x 6 ubuntu ubuntu   4096 Jun 29 08:10 src
-rw-rw-r-- 1 ubuntu ubuntu   1601 Jun 29 08:10 vite.config.js

## 重构计划
1. 分析现有架构和耦合问题
2. 开发AG-UI前端适配器
3. 重构核心组件
4. 测试和验证

## 回滚方案
如需回滚，执行：
```bash
rm -rf powerautomation_web/smartui
cp -r backup/smartui_backup_20250629_081039/smartui powerautomation_web/
```

