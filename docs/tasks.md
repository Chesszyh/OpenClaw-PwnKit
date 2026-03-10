# Dev tasks

1. 本地：机器配置高但没有公网 IP，使用 Cloudflare Tunnel 暴露服务，直接用原项目并持续更新上游修改即可。
2. 远程：部署在 1C1G 云主机上，需进行性能优化和资源限制（可能要修改项目和配置），确保在极低配置下稳定运行。有公网 IP。

请帮我在当前实验环境下部署本项目。机器配置只有1c1g，因此需要完全依赖api而非本地模型，并控制本项目的资源占用。api端点：http://localhost:8317/v1/。可用模型：gpt-5.4, gpt-5.3-codex-spark等。我已完成.venv虚拟环境全部安装。

set_c2 https://pop-dispatched-ship-handmade.trycloudflare.com/
generate honeypot
generate skill
