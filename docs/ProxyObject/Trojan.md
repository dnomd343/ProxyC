## trojanObject

```
{
    'server': ---,
    'port': ---,
    'passwd': ---,
    'stream': ---,
}
```

### server

+ 类型：*str*
+ 说明：Trojan服务地址
+ 缺省：必选
+ 限制：IP地址或域名

### port

+ 类型：*int*
+ 说明：Trojan服务端口
+ 缺省：必选
+ 限制：1 ～ 65535

### passwd

+ 类型：*str*
+ 说明：Trojan连接密码
+ 缺省：必选
+ 限制：无

### stream

+ 类型：[*tcpObject*](#tcpobject) / [*kcpObject*](#kcpobject) / [*wsObject*](#wsobject) / [*h2Object*](#h2object) / [*quicObject*](#quicobject) / [*grpcObject*](#grpcobject)
+ 说明：Trojan传输方式
+ 缺省：`tcpObject`
+ 限制：无

## tcpObject

```
{
    'type': 'tcp',
    'obfs': ---,
    'secure': ---,
}
```

### obfs

+ 类型：*None* / [*obfsObject*](#obfsobject)
+ 说明：http伪装选项
+ 缺省：`None`
+ 限制：无

### secure

+ 类型：*None* / [*tlsObject*](#tlsobject) / [*xtlsObject*](#xtlsobject)
+ 说明：TLS加密选项
+ 缺省：`tlsObject`
+ 限制：无

## kcpObject

```
{
    'type': 'kcp',
    'seed': ---,
    'obfs': ---,
    'secure': ---,
}
```

### seed

+ 类型：*None* / *str*
+ 说明：mKCP混淆密码
+ 缺省：`None`
+ 限制：无

### obfs

+ 类型：*str*
+ 说明：数据包头部伪装类型
+ 缺省：`none`
+ 限制：`none`, `srtp`, `utp`, `wechat-video`, `dtls`, `wireguard`

### secure

+ 类型：*None* / [*tlsObject*](#tlsobject) / [*xtlsObject*](#xtlsobject)
+ 说明：TLS加密选项
+ 缺省：`tlsObject`
+ 限制：无

## wsObject

```
{
    'type': 'ws',
    'host': ---,
    'path': ---,
    'ed': ---,
    'secure': ---,
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

### ed

+ 类型：*None* / *int*
+ 说明：Early Data长度阈值
+ 缺省：`None`
+ 限制：>0

### secure

+ 类型：*None* / [*tlsObject*](#tlsobject)
+ 说明：TLS加密选项
+ 缺省：`tlsObject`
+ 限制：无

## h2Object

```
{
    'type': 'h2',
    'host': ---,
    'path': ---,
    'secure': ---,
}
```

### host

+ 类型：*str*
+ 说明：HTTP/2连接域名
+ 缺省：`空`
+ 限制：无

### path

+ 类型：*str*
+ 说明：HTTP/2连接路径
+ 缺省：`/`
+ 限制：无

### secure

+ 类型：[*tlsObject*](#tlsobject)
+ 说明：TLS加密选项
+ 缺省：`tlsObject`
+ 限制：无

## quicObject

```
{
    'type': 'quic',
    'method': ---,
    'passwd': ---,
    'obfs': ---,
    'secure': ---,
}
```

### method

+ 类型：*str*
+ 说明：QUIC加密方式
+ 缺省：`none`
+ 限制：`none`, `aes-128-gcm`, `chacha20-poly1305`

### passwd

+ 类型：*str*
+ 说明：QUIC连接密码
+ 缺省：`空`
+ 限制：无

### obfs

+ 类型：*str*
+ 说明：数据包头部伪装类型
+ 缺省：`none`
+ 限制：`none`, `srtp`, `utp`, `wechat-video`, `dtls`, `wireguard`

### secure

+ 类型：[*tlsObject*](#tlsobject)
+ 说明：TLS加密选项
+ 缺省：`tlsObject`
+ 限制：无

## grpcObject

```
{
    'type': 'grpc',
    'service': ---,
    'mode': ---,
    'secure': ---,
}
```

### service

+ 类型：*str*
+ 说明：gRPC服务名称
+ 缺省：必选
+ 限制：无

### mode

+ 类型：*str*
+ 说明：gRPC传输模式
+ 缺省：`gun`
+ 限制：`gun`, `multi`

### secure

+ 类型：*None* / [*tlsObject*](#tlsobject)
+ 说明：TLS加密选项
+ 缺省：`tlsObject`
+ 限制：无

## obfsObject

```
{
    'host': ---,
    'path': ---,
}
```

### host

+ 类型：*str*
+ 说明：http伪装域名
+ 缺省：`空`
+ 限制：无

### path

+ 类型：*str*
+ 说明：http伪装路径
+ 缺省：`/`
+ 限制：无

## tlsObject

```
{
    'type': 'tls',
    'sni': ---,
    'alpn': ---,
    'verify': ---,
}
```

### sni

+ 类型：*str*
+ 说明：TLS握手SNI字段
+ 缺省：`obfsObject.host[0]` / `wsObject.host` / `h2Object.host[0]` / `空`
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

## xtlsObject

```
{
    'type': 'xtls',
    'sni': ---,
    'alpn': ---,
    'verify': ---，
    'flow': ---,
    'udp443': ---,
}
```

### sni

+ 类型：*str*
+ 说明：TLS握手SNI字段
+ 缺省：`obfsObject.host[0]` / `wsObject.host` / `h2Object.host[0]` / `空`
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

### flow

+ 类型：*str*
+ 说明：XTLS流控算法
+ 缺省：`xtls-direct`
+ 限制：`xtls-origin`, `xtls-direct`, `xtls-splice`

### udp443

+ 类型：*bool*
+ 说明：是否放行UDP/443端口流量
+ 缺省：`False`
+ 限制：无
