## Brook

> **remark**
> 
> + 类型：*str*
> + 说明：节点备注名称
> + 缺省：''
> + 可选值：不限

```
{
    'type': 'brook',
    'server': ...,
    'port': ...,
    'passwd': ...,
    'ws': ...
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
+ 说明：Brook连接密码
+ 缺省：必选
+ 可选值：不限

**ws**

+ 类型：*None* / *wsObject*
+ 说明：WebSocket传输配置
+ 缺省：None
+ 可选值：不限

### wsObject

```
{
    'host': ...,
    'path': ...,
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

**secure**

+ 类型：*None* / *secureObject*
+ 说明：TLS加密配置
+ 缺省：None
+ 可选值：不限

### secureObject

```
{
    'verify': ...
}
```

**verify**

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：True
+ 可选值：不限
+ 建议值：True
