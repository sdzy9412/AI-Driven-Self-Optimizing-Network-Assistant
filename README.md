# AI-Driven Self-Optimizing Network Assistant

AI驱动的自优化网络助手 - 结合智能故障分析和自动化网络优化的下一代电信运维系统

## 项目简介

本项目演示了如何使用AWS Bedrock AgentCore、Strands Agents和MCP来构建一个自主优化的网络运维系统。系统能够：

- 📊 **实时监控**：多域（RAN/Transport/Core）网络健康监测
- 🤖 **AI推理**：基于AWS Bedrock AgentCore的智能故障根因分析
- ⚡ **自动优化**：自动执行优化动作，支持dry-run和回滚
- 📈 **可视化**：清晰的优化前后指标对比（红色=故障，绿色=优化后）
- 🔒 **安全可控**：置信度阈值和人工审批机制

## 功能特性

### 1. Apple风格玻璃界面
- 毛玻璃效果（glassmorphism）
- 半透明卡片设计
- 柔和阴影和渐变

### 2. 实时时序图
- Plotly交互式图表
- 红色区域：故障（incident）阶段
- 绿色区域：已优化（optimized）阶段
- 多指标叠加显示

### 3. 网络健康度监测
- 综合健康度评分（0-100%）
- 分域健康度统计
- 实时状态指示器

### 4. AWS服务集成（预留接口）
- **Bedrock AgentCore**：智能推理分析
- **DynamoDB**：指标和审计日志存储
- **Lambda**：优化动作执行器
- **CloudWatch**：实时指标拉取

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并配置AWS凭证（如果使用真实AWS服务）：

```bash
cp .env.example .env
```

默认使用Mock模式，无需AWS凭证即可运行。

### 3. 生成演示数据

首次运行会自动生成Mock数据，或手动运行：

```bash
# 设置PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH  # Linux/Mac
# 或
set PYTHONPATH=%CD%;%PYTHONPATH%     # Windows

python services/mock_service.py
```

### 4. 启动Streamlit应用

```bash
streamlit run app.py
```

或者直接访问Dashboard：

```bash
streamlit run pages/dashboard.py
```

浏览器将自动打开 http://localhost:8501

## 项目结构

```
├── app.py                      # Streamlit主入口
├── pages/
│   ├── dashboard.py            # 主Dashboard页面
│   └── __init__.py
├── components/
│   ├── glass_style.py          # 玻璃风格CSS
│   ├── health_indicator.py     # 健康度指示器
│   ├── timeline_chart.py       # 时序图组件
│   ├── kpi_cards.py            # KPI卡片组件
│   └── __init__.py
├── services/
│   ├── data_service.py         # 统一数据服务
│   ├── mock_service.py         # Mock数据生成
│   ├── aws_service.py          # AWS服务接口
│   ├── dynamodb_service.py    # DynamoDB接口
│   └── __init__.py
├── utils/
│   ├── config.py              # 配置管理
│   ├── data_validator.py      # 数据验证器
│   └── __init__.py
├── data/                       # 数据目录（自动生成）
│   ├── mock_metrics.json
│   ├── before_after_metrics.csv
│   └── agentcore_output.json
└── requirements.txt
```

## 数据模型

### NetworkMetric（网络指标）
- `timestamp`: 时间戳（UTC）
- `domain`: 网络域（RAN/Transport/Core/NTN）
- `cell_id` / `link_id`: 资源ID
- `latency_ms`: 延迟（毫秒）
- `packet_loss`: 丢包率（%）
- `utilization_pct`: 利用率（%）
- `throughput_mbps`: 吞吐量（Mbps）
- `energy_kwh`: 能耗（kWh）
- `status`: 状态（normal/incident/optimized）

### AgentCoreOutput（AI分析输出）
- `root_cause`: 根本原因
- `recommended_action`: 推荐动作
- `confidence`: 置信度（0-1）
- `can_auto_execute`: 是否可自动执行
- `expected_impact`: 预期影响

## 演示场景

系统包含两个预定义的故障场景：

### 场景A：RAN小区过载 (cell-A01)
- **Normal**: 延迟 ~50ms，丢包 ~0.1%
- **Incident**: 延迟跳至 300ms+，丢包 5%+，利用率 >90%
- **Optimized**: AI执行流量调度，延迟降至 140ms，丢包降至 2.2%

### 场景B：Transport链路拥塞 (transport-link-B17)
- **Normal**: 延迟 ~55ms，丢包 ~0.2%
- **Incident**: 传输路径故障，延迟 270ms，丢包 4.9%
- **Optimized**: AI执行路由重定向，延迟降至 115ms，丢包降至 1.9%

## 数据一致性

系统实现了完整的数据一致性验证：

- ✅ 时间戳同步（UTC）
- ✅ 状态转换验证（normal → incident → optimized）
- ✅ 域标识一致性（RAN必须提供cell_id，Transport必须提供link_id）
- ✅ 状态机合法性检查

## 运行模式

### Mock模式（默认）
- 使用本地生成的演示数据
- 无需AWS凭证
- 适合演示和开发

### 真实AWS模式
1. 配置 `.env` 文件中的AWS凭证
2. 设置 `USE_MOCK_DATA=false`
3. 确保DynamoDB表已创建
4. 配置Lambda函数和Bedrock访问权限

## 技术栈

- **前端**: Streamlit 1.28+
- **可视化**: Plotly 5.17+
- **数据**: Pandas, NumPy
- **AWS**: boto3 (可选)
- **验证**: Pydantic 2.0+

## 预期影响（Mock KPIs）

- **MTTR** ↓ 50%：从手动30+分钟降至<5分钟
- **网络可用性** ↑ 30%：自动故障恢复
- **能耗** ↓ 10%：智能负载均衡
- **AI置信度** ≥ 0.7：透明、可解释的决策

## 许可证

MIT License

## 作者

YiZhang - Hackathon for HAT
