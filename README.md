# ProxyC

> 强大的代理工具集，支持几乎所有科学上网协议

✅完整的协议与选项支持：

+ `Shadowsocks`：支持[69种](./docs/ProxyObject/Shadowsocks.md#method)加密方式，[12种](./docs/ProxyObject/Shadowsocks.md#type)SIP003插件

+ `ShadowsocksR`：支持[37种](./docs/ProxyObject/ShadowsocksR.md#method)加密方式，[17种](./docs/ProxyObject/ShadowsocksR.md#protocol)传输协议，[7种](./docs/ProxyObject/ShadowsocksR.md#obfs)混淆方式

+ `VMess`：完整的V2ray内核适配，支持[5种](./docs/ProxyObject/VMess.md#method)加密方式，支持TLS，支持以下传输方式

  + `TCP`：支持obfs混淆
  + `mKCP`：支持密码混淆，[6种](./docs/ProxyObject/VMess.md#obfs-1)数据包伪装方式
  + `WebSocket`：支持0-RTT连接
  + `HTTP/2`：支持自定义域名和路径
  + `QUIC`：支持[3种](./docs/ProxyObject/VMess.md#method-1)加密方式，[6种](./docs/ProxyObject/VMess.md#obfs-2)数据包伪装
  + `gRPC`：支持 `gun` 与 `multi` 两种模式

+ `VLESS`：完整的Xray内核适配，支持TLS与XTLS，支持的传输方式同上

+ `Trojan`：完整的Xray内核适配，支持TLS与XTLS，支持的传输方式同上

+ `Trojan-Go`：支持WebSocket连接，Shadowsocks加密连接，TLS加密，[12种](./docs/ProxyObject/TrojanGo.md#type)SIP003插件

+ `Brook`：支持UoT开启，WebSocket传输，TLS加密，原始数据传输

+ `Hysteria`：支持 `udp`, `wechat-video`, `faketcp` 连接，支持混淆与密码验证

+ `Relay`：待支持

+ `Snell`：待支持

+ `RelayBaton`：待支持

+ `PingTunnel`：待支持

+ `NaiveProxy`：待支持

+ `WireGuard`：待支持

+ `SSH`：待支持
