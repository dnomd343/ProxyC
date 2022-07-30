## brookObject

```
{
    'server': ---,
    'port': ---,
    'passwd': ---,
    'ws': ---,
}
```

### server

+ 类型：*str*
+ 说明：Brook服务地址
+ 缺省：必选
+ 限制：IP地址或域名

### port

+ 类型：*int*
+ 说明：Brook服务端口
+ 缺省：必选
+ 限制：1 ～ 65535

### passwd

+ 类型：*str*
+ 说明：Brook连接密码
+ 缺省：必选
+ 限制：无

### ws

+ 类型：*None* / [*wsObject*](#wsobject)
+ 说明：WebSocket传输配置
+ 缺省：`None`
+ 限制：无

## wsObject

```
{
    'host': ---,
    'path': ---,
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

### secure

+ 类型：*None* / [*secureObject*](#secureobject)
+ 说明：TLS加密配置
+ 缺省：`None`
+ 限制：无

## secureObject

```
{
    'verify': ---,
}
```

### verify

+ 类型：*bool*
+ 说明：是否验证服务端证书
+ 缺省：`True`
+ 限制：无
