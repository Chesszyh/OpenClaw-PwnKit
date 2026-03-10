#!/bin/bash

# 1. 严格限制多线程，防止 CPU 抢占和内存膨胀
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# 2. 强制使用 CPU 模式并禁用不必要的后端缓存
export CUDA_VISIBLE_DEVICES=""
export TORCH_CPU_ONLY=1

# 3. 设置 Huggingface 离线/节省模式 (gpt2 tokenizer 仅需几MB)
export HF_HUB_OFFLINE=0

# 4. 激活虚拟环境并启动
source .venv/bin/activate
echo "[*] Starting OpenClaw-PwnKit on 1C1G node..."
python3 pwnkit_cli.py
