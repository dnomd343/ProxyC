# ProxyC

> 强大的代理工具集，支持几乎所有科学上网协议

&emsp;✅ 全面的代理协议与选项，覆盖几乎所有类型节点

&emsp;⏳ 订阅解析，支持几乎所有客户端配置文件的解码

&emsp;⏳ 延迟测试，IP信息，UDP状态，线路架构分析

&emsp;⏳ 流媒体支持状态、所属地区、CDN分配等检测

&emsp;⏳ 基于RESTful API驱动，方便外围扩展

&emsp;✅ MIT协议开源，无任何使用限制

## 协议支持状态

+ `Shadowsocks`：[69种](./docs/ProxyObject/Shadowsocks.md#method)加密方式，[12种](./docs/ProxyObject/Shadowsocks.md#type)SIP003插件

+ `ShadowsocksR`：[37种](./docs/ProxyObject/ShadowsocksR.md#method)加密方式，[17种](./docs/ProxyObject/ShadowsocksR.md#protocol)传输协议，[7种](./docs/ProxyObject/ShadowsocksR.md#obfs)混淆方式

+ `VMess`：完整的V2ray内核适配，[5种](./docs/ProxyObject/VMess.md#method)加密方式，支持TLS，支持以下传输方式

  + `TCP`：支持obfs混淆
  + `mKCP`：支持密码混淆，[6种](./docs/ProxyObject/VMess.md#obfs-1)数据包伪装方式
  + `WebSocket`：支持0-RTT连接
  + `HTTP/2`：支持自定义域名和路径
  + `QUIC`：支持[3种](./docs/ProxyObject/VMess.md#method-1)加密方式，[6种](./docs/ProxyObject/VMess.md#obfs-2)数据包伪装
  + `gRPC`：支持 `gun` 与 `multi` 模式

+ `VLESS`：完整的Xray内核适配，支持TLS与XTLS，传输方式同上

+ `Trojan`：完整的Xray内核适配，支持TLS与XTLS，传输方式同上

+ `Trojan-Go`：WebSocket连接，Shadowsocks加密连接，TLS加密，[12种](./docs/ProxyObject/TrojanGo.md#type)SIP003插件

+ `Brook`：UoT选项，WebSocket传输，TLS加密，原始数据传输

+ `Hysteria`：[3种](./docs/ProxyObject/Hysteria.md#protocol)连接方式，数据包混淆，密码验证

+ `Relay`：待支持

+ `Snell`：待支持

+ `RelayBaton`：待支持

+ `PingTunnel`：待支持

+ `NaiveProxy`：待支持

+ `WireGuard`：待支持

+ `SSH`：待支持

## 解码支持状态

WIP...

## 功能支持状态

WIP...

## 使用教程

WIP...

## 许可证

MIT ©2022 [@dnomd343](https://github.com/dnomd343)
