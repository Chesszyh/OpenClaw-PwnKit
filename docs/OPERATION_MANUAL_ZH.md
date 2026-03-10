# OpenClaw-PwnKit 操作手册 (1C1G 优化版)

OpenClaw-PwnKit 是一个针对大语言模型 (LLM) 代理 (Agent) 的渗透测试框架，旨在利用 Agent 的工具调用 (Tool-call) 机制实现远程代码执行 (RCE) 和 C2 控制。

---

## 一、 环境要求与安装

### 1. 硬件适配
本项目已针对 **1C1G (1核CPU, 1GB内存)** 的极低功耗云主机进行深度优化。
- **内存优化**：完全依赖远程 API 进行推理，本地仅保留分词器与轻量化向量索引。
- **并发控制**：强制单线程模式，防止系统因过载导致 OOM 或死机。

### 2. 依赖安装
推荐使用 Python 3.10+ 环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 二、 配置说明 (`config.yaml`)

在启动前，请确保配置文件已正确设置：

```yaml
c2_server:
  host: "0.0.0.0"
  port: 8000
  # 重要：修改为你的公网 IP 或域名，否则 Payload 无法回连
  public_url: "http://<YOUR_IP>:8000"

openai:
  # 使用提供的 API 端点
  api_key: "sk-your-key" 
  base_url: "http://localhost:8317/v1/"
  model: "gpt-5.4"
  codex_model: "gpt-5.3-codex-spark"

optimization:
  surrogate_model: "api-only"  # 1C1G 环境必须保持为 api-only
```

---

## 三、 启动与运行

使用内置的优化脚本启动，该脚本会自动注入资源限制环境变量：

```bash
chmod +x run_optimized.sh
./run_optimized.sh
```

---

## 四、 核心功能详解

### 1. 诱饵生成 (`generate`)
通过注入“幻觉触发器”生成攻击载荷。

- **生成 Nginx 蜜罐**：
  ```bash
  PwnKit > generate honeypot "web-proxy-config"
  ```
  生成包含恶意指令的 Nginx 配置文件。当目标 Agent 尝试“修复”或“应用”此配置时，会触发回连。

- **生成带毒技能 (`Poisoned Skill`)**：
  ```bash
  PwnKit > generate skill "DataAnalysisTool" "data-analysis"
  ```
  创建一个看似合法的 Python 技能插件。一旦目标框架加载此插件，攻击者即可获得控制权。

### 2. 攻击算法：CMA-ES 幻觉触发
本项目包含一个高级算法模块 (`attacks/method2_cma_es.py`)：
- **原理**：利用遗传算法在连续向量空间内搜索能最大概率诱导 LLM 触发 `bash` 工具调用的 Token 序列。
- **资源表现**：在 1C1G 环境下，程序会使用随机嵌入矩阵 + PCA 降维技术，将内存占用控制在 200MB 左右。

### 3. 会话管理 (`sessions`)
查看已上线的 Agent 列表：
```bash
PwnKit > sessions
```

### 4. 远程交互 (`interact`)
像使用 SSH 一样直接控制受害者环境：
```bash
PwnKit > interact <Target_ID>
# 示例命令
target@agent$ whoami
target@agent$ ls /etc/shadow
```

---

## 五、 后台管理与批量控制

退出 CLI 界面后，您可以使用 `bot_manager.py` 进行数据库管理：

- **查看完整数据库**：`python3 bot_manager.py list`
- **全平台指令广播**：`python3 bot_manager.py mass_cmd -c "id"`
- **清理数据库**：`python3 bot_manager.py clean`

---

## 六、 常见问题 (FAQ)

**Q: 报错 `[Errno 98] Address already in use` 怎么办？**
A: 端口 8000 被占用。执行 `lsof -i :8000` 找到 PID 并用 `kill -9 <PID>` 杀掉，或在 `config.yaml` 中修改端口。

**Q: 1C1G 环境下运行依然缓慢？**
A: 检查 API 响应速度。本地 CPU 主要消耗在 FAISS 索引构建阶段（仅启动时一次），之后均为 API 网络开销。

**Q: 目标 Agent 没反应？**
A: 确认 `config.yaml` 中的 `public_url` 是否为外网可访问地址。如果是本地测试，请确保 Agent 也在同一内网。
