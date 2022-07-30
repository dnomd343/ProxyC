## trojanGoObject

```
{
    'server': ---,
    'port': ---,
    'passwd': ---,
    'sni': ---,
    'alpn': ---,
    'verify': ---,
    'ws': ---,
    'ss': ---,
    'plugin': ---,
}
```

### server

+ 类型：*str*
+ 说明：TrojanGo服务地址
+ 缺省：必选
+ 限制：IP地址或域名

### port

+ 类型：*int*
+ 说明：TrojanGo服务端口
+ 缺省：必选
+ 限制：1 ～ 65535

### passwd

+ 类型：*str*
+ 说明：TrojanGo连接密码
+ 缺省：必选
+ 限制：无

### sni

+ 类型：*str*
+ 说明：TLS握手SNI字段
+ 缺省：`无`
+ 限制：无

### alpn

+ 类型：*None* / *str*
+ 说明：TLS握手协商协议
+ 缺省：`None`
+ 限制：`h2`, `http/1.1`, `h2,http/1.1`

### verify

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：`True`
+ 限制：无

### ws

+ 类型：*None* / [*wsObject*](#wsobject)
+ 说明：WebSocket连接配置
+ 缺省：`None`
+ 限制：无

### ss

+ 类型：*None* / [*ssObject*](#ssobject)
+ 说明：Shadowsocks加密配置
+ 缺省：`None`
+ 限制：无

### plugin

+ 类型：*None* / [*pluginObject*](#pluginobject)
+ 说明：SIP003插件选项
+ 缺省：`None`
+ 限制：无

## wsObject

```
{
    'host': ---,
    'path': ---,
}
```

### host

+ 类型：*str*
+ 说明：WebSocket连接域名
+ 缺省：`空`
+ 限制：无

### path

+ 类型：*str*
+ 说明：WebSocket连接路径
+ 缺省：`/`
+ 限制：无

## ssObject

```
{
    'method': ---,
    'passwd': ---,
}
```

### method

+ 类型：*str*
+ 说明：Shadowsocks流加密方式
+ 缺省：`aes-128-gcm`
+ 限制：`aes-128-gcm`, `aes-256-gcm`, `chacha20-ietf-poly1305`

### passwd

+ 类型：*str*
+ 说明：Shadowsocks密码
+ 缺省：`空`
+ 限制：无

## pluginObject

```
{
    'type': ---,
    'param': ---,
}
```

### type

+ 类型：*str*
+ 说明：SIP003插件名称
+ 缺省：必选
+ 限制：（以下12种插件名称）

`obfs-local`, `simple-tls`

`kcptun-client`, `qtun-client`, `gun-plugin`

`v2ray-plugin`, `xray-plugin`, `gost-plugin`

`ck-client`, `gq-client`, `mtt-client`, `rabbit-plugin`

### param

+ 类型：*str*
+ 说明：SIP003插件参数
+ 缺省：`空`
+ 限制：无
