## Hysteria

> **remark**
> 
> + 类型：*str*
> + 说明：节点备注名称
> + 缺省：''
> + 可选值：不限

```
{
    'type': 'hysteria',
    'server': ...,
    'port': ...,
    'protocol': ...,
    'obfs': ...,
    'auth': ...,
    'sni': ...,
    'alpn': ...,
    'verify': ...
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

**protocol**

+ 类型：*str*
+ 说明：Hysteria连接方式
+ 缺省：'udp'
+ 可选值：`udp`,`wechat-video`,`faketcp`

**obfs**

+ 类型：*None* / *str*
+ 说明：Hysteria混淆密码
+ 缺省：None
+ 可选值：不限

**auth**

+ 类型：*None* / *str*
+ 说明：Hysteria验证密码
+ 缺省：None
+ 可选值：不限

**sni**

+ 类型：*str*
+ 说明：TLS握手SNI字段
+ 缺省： ''
+ 可选值：不限
+ 建议值：合法域名

**alpn**

+ 类型：*None* / *str*
+ 说明：TLS握手协商协议
+ 缺省：None
+ 可选值：不限

**verify**

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：True
+ 可选值：不限
+ 建议值：True
