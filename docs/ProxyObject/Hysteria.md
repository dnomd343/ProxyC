## hysteriaObject

```
{
    'server': ---,
    'port': ---,
    'protocol': ---,
    'upMbps': ---,
    'downMbps': ---,
    'obfs': ---,
    'auth': ---,
    'sni': ---,
    'alpn': ---,
    'verify': ---,
}
```

### server

+ 类型：*str*
+ 说明：Hysteria服务地址
+ 缺省：必选
+ 限制：IP地址或域名

### port

+ 类型：*int*
+ 说明：Hysteria服务端口
+ 缺省：必选
+ 限制：1 ～ 65535

### protocol

+ 类型：*str*
+ 说明：Hysteria连接方式
+ 缺省：`udp`
+ 限制：`udp`, `wechat-video`, `faketcp`

### upMbps

+ 类型：*int*
+ 说明：Hysteria最大上行速率
+ 缺省：`10`
+ 限制：>0

### downMbps

+ 类型：*int*
+ 说明：Hysteria最大下行速率
+ 缺省：`50`
+ 限制：>0

### obfs

+ 类型：*None* / *str*
+ 说明：Hysteria混淆密码
+ 缺省：`None`
+ 限制：无

### auth

+ 类型：*None* / *str*
+ 说明：Hysteria验证密码
+ 缺省：`None`
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
+ 限制：无

### verify

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：`True`
+ 限制：无
