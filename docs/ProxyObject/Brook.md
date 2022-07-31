## brookObject

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

### stream

+ 类型：[*originObject*](#originobject) / [*wsObject*](#wsobject)
+ 说明：Brook传输方式
+ 缺省：`originObject`
+ 限制：无

## originObject

```
{
    'type': 'origin',
    'uot': ---,
}
```

### uot

+ 类型：*bool*
+ 说明：UDP over TCP
+ 缺省：`False`
+ 限制：无

## wsObject

```
{
    'type': 'ws',
    'host': ---,
    'path': ---,
    'raw': ---,
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
+ 缺省：`/ws`
+ 限制：无

### raw

+ 类型：*bool*
+ 说明：是否直接传输原始数据（即`--withoutBrookProtocol`）
+ 缺省：`False`
+ 限制：无

### secure

+ 类型：*None* / [*secureObject*](#secureobject)
+ 说明：TLS加密选项
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
