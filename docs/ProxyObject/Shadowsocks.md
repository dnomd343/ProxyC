## Shadowsocks

> **remark**
> 
> + 类型：*str*
> + 说明：节点备注名称
> + 缺省：''
> + 可选值：不限

```
{
    'type': 'ss',
    'server': ...,
    'port': ...,
    'method': ...,
    'passwd': ...,
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

**method**

+ 类型：*str*
+ 说明：Shadowsocks加密方式
+ 缺省：必选
+ 可选值：`aes-128-gcm`,`aes-192-gcm`,`aes-256-gcm`,`aes-128-ctr`,`aes-192-ctr`,`aes-256-ctr`,`aes-128-ocb`,`aes-192-ocb`,`aes-256-ocb`,`aes-128-ofb`,`aes-192-ofb`,`aes-256-ofb`,`aes-128-cfb`,`aes-192-cfb`,`aes-256-cfb`,`aes-128-cfb1`,`aes-192-cfb1`,`aes-256-cfb1`,`aes-128-cfb8`,`aes-192-cfb8`,`aes-256-cfb8`,`aes-128-cfb128`,`aes-192-cfb128`,`aes-256-cfb128`,`camellia-128-cfb`,`camellia-192-cfb`,`camellia-256-cfb`,`camellia-128-cfb128`,`camellia-192-cfb128`,`camellia-256-cfb128`,`plain`,`none`,`table`,`rc4`,`rc4-md5`,`rc2-cfb`,`bf-cfb`,`cast5-cfb`,`des-cfb`,`idea-cfb`,`seed-cfb`,`salsa20`,`salsa20-ctr`,`xchacha20`,`chacha20`,`chacha20-ietf`,`chacha20-poly1305`,`chacha20-ietf-poly1305`,`xchacha20-ietf-poly1305`
+ 建议值：`aes-256-gcm`,`aes-128-gcm`,`chacha20-ietf-poly1305`

**passwd**

+ 类型：*str*
+ 说明：Shadowsocks连接密码
+ 缺省：必选
+ 可选值：不限

**plugin**

+ 类型：*None* / *pluginObject*
+ 说明：SIP003插件
+ 缺省：None
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
