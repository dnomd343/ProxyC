## Trojan

> **remark**
> 
> + 类型：*str*
> + 说明：节点备注名称
> + 缺省：''
> + 可选值：不限

```
{
    'type': 'trojan',
    'server': ...,
    'port': ...,
    'passwd': ...,
    'stream': ...
}
```

**server**

+ 类型：*str*
+ 说明：服务器地址
+ 缺省：必选
+ 可选值：合法的IP地址或域名

**port**

+ 类型：*int*
+ 说明：服务器端口
+ 缺省：必选
+ 可选值：1 ～ 65535

**passwd**

+ 类型：*str*
+ 说明：Trojan连接密码
+ 缺省：必选
+ 可选值：不限

**stream**

+ 类型：*tcpObject* / *kcpObject* / *wsObject* / *h2Object* / *quicObject* / *grpcObject*
+ 说明：Trojan底层传输方式
+ 缺省：tcpObject
+ 可选值：不限

### tcpObject

```
{
    'type': 'tcp',
    'obfs': ...,
    'secure': ...
}
```

**obfs**

+ 类型：*None* / *obfsObject*
+ 说明：http伪装
+ 缺省：None
+ 可选值：不限

**secure**

+ 类型：*None* / *tlsObject* / *xtlsObject*
+ 说明：TLS加密
+ 缺省：tlsObject
+ 可选值：不限

### kcpObject

```
{
    'type': 'kcp',
    'seed': ...,
    'obfs': ...,
    'secure': ...
}
```

**seed**

+ 类型：*None* / *str*
+ 说明：mKCP混淆密码
+ 缺省：None
+ 可选值：不限

**obfs**

+ 类型：*str*
+ 说明：数据包头部伪装类型
+ 缺省：'none'
+ 可选值：`none`,`srtp`,`utp`,`wechat-video`,`dtls`,`wireguard`

**secure**

+ 类型：*None* / *tlsObject* / *xtlsObject*
+ 说明：TLS加密
+ 缺省：tlsObject
+ 可选值：不限

### wsObject

```
{
    'type': 'ws',
    'host': ...,
    'path': ...,
    'ed': ...,
    'secure': ...
}
```

**host**

+ 类型：*str*
+ 说明：Websocket连接域名
+ 缺省：''
+ 可选值：不限
+ 建议值：合法域名

**path**

+ 类型：*str*
+ 说明：Websocket连接路径
+ 缺省：'/'
+ 可选值：不限
+ 建议值：以`/`开头的合法路径

**ed**

+ 类型：*None* / *int*
+ 说明：`Early Data`长度阈值
+ 缺省：None
+ 可选值：>0
+ 建议值：2048

**secure**

+ 类型：*None* / *tlsObject*
+ 说明：TLS加密
+ 缺省：tlsObject
+ 可选值：不限

### h2Object

```
{
    'type': 'h2',
    'host': ...,
    'path': ...,
    'secure': ...
}
```

**host**

+ 类型：*str*
+ 说明：HTTP/2通讯域名
+ 缺省：''
+ 可选值：不限
+ 建议值：合法域名列表（逗号隔开）

**path**

+ 类型：*str*
+ 说明：HTTP/2通讯路径
+ 缺省：'/'
+ 可选值：不限
+ 建议值：以`/`开头的合法路径

**secure**

+ 类型：*tlsObject*
+ 说明：TLS加密
+ 缺省：tlsObject
+ 可选值：不限

### quicObject

```
{
    'type': 'quic',
    'method': ...,
    'passwd': ...,
    'obfs': ...,
    'secure': ...
}
```

**method**

+ 类型：*str*
+ 说明：QUIC加密方式
+ 缺省：'none'
+ 可选值：`none`,`aes-128-gcm`,`chacha20-poly1305`

**passwd**

+ 类型：*str*
+ 说明：QUIC连接密码
+ 缺省：''
+ 可选值：不限

**obfs**

+ 类型：*str*
+ 说明：数据包头部伪装类型
+ 缺省：'none'
+ 可选值：`none`,`srtp`,`utp`,`wechat-video`,`dtls`,`wireguard`

**secure**

+ 类型：*tlsObject*
+ 说明：TLS加密
+ 缺省：tlsObject
+ 可选值：不限

### grpcObject

```
{
    'type': 'grpc',
    'service': ...,
    'mode': ...,
    'secure': ...
}
```

**service**

+ 类型：*str*
+ 说明：gRPC服务名称
+ 缺省：必选
+ 可选值：不限
+ 建议值：英文大小写字母、数字、下划线及英文句号组成

**mode**

+ 类型：*str*
+ 说明：gRPC传输模式
+ 缺省：'gun'
+ 可选值：`gun`,`multi`
+ 建议值：'multi'

**secure**

+ 类型：*None* / *tlsObject*
+ 说明：TLS加密
+ 缺省：tlsObject
+ 可选值：不限

### obfsObject

```
{
    'host': ...,
    'path': ...
}
```

**host**

+ 类型：*str*
+ 说明：http伪装域名
+ 缺省：''
+ 可选值：不限
+ 建议值：合法域名列表（逗号隔开）

**path**

+ 类型：*str*
+ 说明：http伪装路径
+ 缺省：'/'
+ 可选值：不限
+ 建议值：以`/`开头的合法路径

### tlsObject

```
{
    'type': 'tls',
    'sni': ...,
    'alpn': ...,
    'verify': ...
}
```

**sni**

+ 类型：*str*
+ 说明：TLS握手SNI字段
+ 缺省：obfsObject.host[0] / wsObject.host / h2Object.host[0] / ''
+ 可选值：不限
+ 建议值：合法域名

**alpn**

+ 类型：*None* / *str*
+ 说明：TLS握手协商协议
+ 缺省：None
+ 可选值：`h2`,`http/1.1`,`h2,http/1.1`
+ 建议值：'h2,http/1.1'

**verify**

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：True
+ 可选值：不限
+ 建议值：True

### xtlsObject

```
{
    'type': 'xtls',
    'sni': ...,
    'alpn': ...,
    'verify': ...，
    'flow': ...,
    'udp443': ...
}
```

**sni**

+ 类型：*str*
+ 说明：TLS握手SNI字段
+ 缺省：obfsObject.host[0] / wsObject.host / h2Object.host[0] / ''
+ 可选值：不限
+ 建议值：合法域名

**alpn**

+ 类型：*None* / *str*
+ 说明：TLS握手协商协议
+ 缺省：None
+ 可选值：`h2`,`http/1.1`,`h2,http/1.1`
+ 建议值：'h2,http/1.1'

**verify**

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：True
+ 可选值：不限
+ 建议值：True

**flow**

+ 类型：*str*
+ 说明：XTLS流控算法
+ 缺省：'xtls-direct'
+ 可选值：`xtls-origin`,`xtls-direct`,`xtls-splice`
+ 建议值：'xtls-direct' (Linux平台建议`xtls-splice`)

**udp443**

+ 类型：*bool*
+ 说明：是否放行UDP/443端口流量
+ 缺省：False
+ 可选值：不限
+ 建议值：False
