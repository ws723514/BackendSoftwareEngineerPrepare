# 变更日志

⚠️ **版本说明**: 由于本项目位于主仓库 `BackendSoftwareEngineerPrepare` 中，所有版本标签使用 `grpc-` 前缀以避免冲突。

## [grpc-v1.0.0] - 2024-01-XX (当前版本)

### ✨ 新增功能
- 实现 gRPC 基础通讯功能
- 添加 SendTelemetry 单向发送接口
- 添加 GetTelemetry 单向查询接口
- 内存存储的遥测数据管理
- 完整的 protobuf 代码生成和导入修复

### 🔧 技术改进
- 建立清晰的项目结构
- 使用 Buf 工具链管理 protobuf
- 创建完整的测试脚本
- 编写详细的学习文档和运行指南

### 📚 文档
- 创建 `learningProgress.md` 学习进度文档
- 创建 `新版-运行指南.md` 运行指南
- 创建 `学习与实现_ToDo_List.md` 任务清单
- 创建 `VERSION_MANAGEMENT.md` 版本管理策略

### 🏗️ 项目结构
```
RealTimeDataMonitorDemoRewritebyHand/
├── app/
│   ├── grpc_server.py           # gRPC服务器
│   ├── grpc_client.py           # gRPC客户端
│   └── __init__.py
├── test/
│   ├── server.py                # 测试服务器
│   ├── test_communication.py    # 通讯测试
│   └── __init__.py
├── generated/
│   └── telemetry/v1/
│       ├── telemetry_pb2.py     # 生成的protobuf消息
│       └── telemetry_pb2_grpc.py # 生成的gRPC服务
├── scripts/
│   ├── tag_version.sh           # 版本标记脚本
│   └── show_versions.sh         # 版本查看脚本
└── 文档文件...
```

### 🧪 测试
- 自动化测试脚本验证 gRPC 通讯
- 手动测试验证客户端-服务器交互
- 错误处理测试

---

## 计划中的版本

### [grpc-v1.1.0] - 计划中
- 🔄 添加 SubscribeTelemetry 服务器流式推送功能
- 🔄 实现实时数据订阅机制
- 🔄 完善流式通讯的错误处理

### [grpc-v1.2.0] - 计划中  
- 🔄 添加 StreamTelemetry 双向流功能
- 🔄 实现客户端-服务器双向实时通讯
- 🔄 完善双向流的生命周期管理

### [grpc-v2.0.0] - 计划中
- 🔄 集成 Redis 替代内存存储
- 🔄 支持多进程数据共享
- 🔄 实现数据持久化

### [grpc-v3.0.0] - 计划中
- 🔄 Docker 容器化部署
- 🔄 Docker Compose 多服务编排
- 🔄 容器网络配置

### [grpc-v4.0.0] - 计划中
- 🔄 多进程/多服务部署
- 🔄 负载均衡和服务发现
- 🔄 分布式架构设计

### [grpc-v5.0.0] - 计划中
- 🔄 认证鉴权系统
- 🔄 监控告警 (Prometheus + Grafana)
- 🔄 CI/CD 自动化部署
- 🔄 云原生 (Kubernetes) 部署

---

## 版本说明

- **版本格式**: 遵循语义化版本控制 (Semantic Versioning)
- **主版本**: 对应学习计划的5个主要阶段
- **次版本**: 新功能添加 (向后兼容)
- **修订版本**: 问题修复 (向后兼容)

## 如何查看版本

```bash
# 查看所有版本
git tag --list

# 查看当前版本
git describe --tags --abbrev=0

# 查看版本详情
git show v1.0.0

# 使用脚本查看
./scripts/show_versions.sh
``` 