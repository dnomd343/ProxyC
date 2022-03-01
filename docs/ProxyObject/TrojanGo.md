## Trojan-Go

> **remark**
> 
> + 类型：*str*
> + 说明：节点备注名称
> + 缺省：''
> + 可选值：不限

```
{
    'type': 'trojan-go',
    'server': ...,
    'port': ...,
    'passwd': ...,
    'sni': ...,
    'alpn': ...,
    'verify': ...,
    'ws': ...,
    'ss': ...,
    'plugin': ...
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
+ 可选值：`h2`,`http/1.1`,`h2,http/1.1`
+ 建议值：'h2,http/1.1'

**verify**

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：True
+ 可选值：不限
+ 建议值：True

**ws**

+ 类型：*None* / *wsObject*
+ 说明：WebSocket连接配置
+ 缺省：None
+ 可选值：不限

**ss**

+ 类型：*None* / *ssObject*
+ 说明：Shadowsocks加密配置
+ 缺省：None
+ 可选值：不限

**plugin**

+ 类型：*None* / *pluginObject*
+ 说明：SIP003插件
+ 缺省：None
+ 可选值：不限

### wsObject

```
{
    'host': ...,
    'path': ...
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

### ssObject

```
{
    'method': ...,
    'passwd': ...
}
```

**method**

+ 类型：*str*
+ 说明：Shadowsocks流加密方式
+ 缺省：'AES-128-GCM'
+ 可选值：`AES-128-GCM`,`AES-256-GCM`,`CHACHA20-IETF-POLY1305`
+ 建议值：x86平台使用AES方式，ARM平台使用CHACHA20方式

**passwd**

+ 类型：*str*
+ 说明：Shadowsocks密码
+ 缺省：''
+ 可选值：不限

### pluginObject

```
{
    'type': ...,
    'param': ...
}
```

**type**

+ 类型：*str*
+ 说明：SIP003插件名称
+ 缺省：必选
+ 可选值：`obfs-local`,`simple-tls`,`v2ray-plugin`,`xray-plugin`,`kcptun-client`,`gost-plugin`,`ck-client`,`gq-client`,`mtt-client`,`rabbit-plugin`,`qtun-client`,`gun-plugin`

**param**

+ 类型：*str*
+ 说明：SIP003插件参数
+ 缺省：''
+ 可选值：不限
