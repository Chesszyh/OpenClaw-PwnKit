# cloudflared tunnel 排障报告

日期: 2026-03-11

## 现象

执行以下命令时，`cloudflared` 连接不稳定或报错:

```bash
cloudflared tunnel --url http://localhost:8000
```

后续改为:

```bash
env -u all_proxy -u http_proxy -u https_proxy \
cloudflared tunnel --protocol http2 --url http://localhost:8000
```

公网地址可访问，但页面显示:

```json
{"detail":"Not Found"}
```

## 结论

页面显示 `{"detail":"Not Found"}` 是正常的。

原因不是 `cloudflared` 故障，而是本地服务 `http://localhost:8000/` 根路径本身返回的就是 `404 Not Found`，且响应体为 JSON。公网 tunnel 只是把这个结果转发了出去。

## 根因分析

本次问题实际由两部分组成:

1. `clash-verge-rev` 开启了 TUN 模式，`cloudflared` 进程流量被代理接管，导致连接 Cloudflare edge 时出现异常。
2. 当前网络环境下，`cloudflared` 默认优先使用的 `QUIC` 不稳定，需要强制切换到 `HTTP/2`。

## 关键现象

### 1. 本地服务正常

本地检查 `localhost:8000` 可访问，返回头部类似:

```http
HTTP/1.1 404 Not Found
Server: uvicorn
Content-Type: application/json
```

这说明:

- 8000 端口上的服务是正常启动的
- 根路径 `/` 没有对应路由，所以返回 404

### 2. 默认 `quic` 失败

直接执行:

```bash
cloudflared tunnel --url http://localhost:8000
```

会出现类似错误:

```text
failed to dial to edge with quic: timeout: no recent network activity
```

说明默认的 `QUIC/UDP` 路径在当前网络中不可用或不稳定。

### 3. `http2` 可成功建立连接

改用`env -u all_proxy -u http_proxy -u https_proxy` 强制不使用系统代理，并指定 `--protocol http2` ：

```bash
env -u all_proxy -u http_proxy -u https_proxy \ 
cloudflared tunnel --protocol http2 --url http://localhost:8000
```

日志中出现:

```text
Registered tunnel connection ... protocol=http2
```

说明 tunnel 已成功建立。

## Clash Verge 持久修复

为避免 `cloudflared` 再次被 TUN 接管，已在 Clash Verge 的增强配置中加入持久规则:

### 文件 1

`/home/chesszyh/.local/share/io.github.clash-verge-rev.clash-verge-rev/profiles/md3vwVh0HaoX.yaml`

加入:

```yaml
find-process-mode: strict
```

### 文件 2

`/home/chesszyh/.local/share/io.github.clash-verge-rev.clash-verge-rev/profiles/ryguEitH4tBd.yaml`

加入:

```yaml
prepend:
  - PROCESS-NAME,cloudflared,DIRECT
```

该规则重载后会体现在运行配置 `clash-verge.yaml` 中。

## 关于 `Unauthorized: Tunnel not found`

在 quick tunnel 创建初期，日志里短暂出现:

```text
Unauthorized: Tunnel not found
```

如果随后出现:

```text
Registered tunnel connection
```

则说明只是 Cloudflare 边缘节点的短暂同步/重试过程，不影响最终使用。

## 最终可用命令

建议固定使用:

```bash
env -u all_proxy -u http_proxy -u https_proxy \
cloudflared tunnel --protocol http2 --url http://localhost:8000
```

## 如何判断是否正常

满足以下两点即可认为 tunnel 工作正常:

1. `cloudflared` 日志中出现 `Registered tunnel connection`
2. 访问 `trycloudflare.com` 分配的地址时，能看到与你本地服务一致的返回结果

如果公网地址显示:

```json
{"detail":"Not Found"}
```

则表示 tunnel 正常，只是你本地应用的 `/` 路径没有定义。

## 后续建议

如果希望公网打开后不是 `{"detail":"Not Found"}`，需要修改本地 8000 服务本身，例如:

- 为 `/` 增加路由
- 改为转发到已有页面路径，例如 `/docs`、`/api/...`
- 或让 `cloudflared` 指向实际有内容的本地地址

