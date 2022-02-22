# 代理节点格式

```
{
    'type': ...,
    ...
}
```

**type**

+ 类型：*str*

+ 说明：节点类型

+ 缺省：必选

+ 可选值：`ss`,`ssr`

## Shadowsocks

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

## ShadowsocksR

```
{
    'type': 'ssr',
    'server': ...,
    'port': ...,
    'method': ...,
    'passwd': ...,
    'protocol': ...,
    'protocolParam': ...,
    'obfs': ...,
    'obfsParam': ...
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

+ 说明：ShadowsocksR加密方式

+ 缺省：必选

+ 可选值：`aes-128-cfb`,`aes-192-cfb`,`aes-256-cfb`,`aes-128-cfb1`,`aes-192-cfb1`,`aes-256-cfb1`,`aes-128-cfb8`,`aes-192-cfb8`,`aes-256-cfb8`,`aes-128-ctr`,`aes-192-ctr`,`aes-256-ctr`,`aes-128-gcm`,`aes-192-gcm`,`aes-256-gcm`,`aes-128-ofb`,`aes-192-ofb`,`aes-256-ofb`,`camellia-128-cfb`,`camellia-192-cfb`,`camellia-256-cfb`,`none`,`table`,`rc4`,`rc4-md5`,`rc4-md5-6`,`bf-cfb`,`cast5-cfb`,`des-cfb`,`idea-cfb`,`seed-cfb`,`rc2-cfb`,`salsa20`,`xsalsa20`,`chacha20`,`xchacha20`,`chacha20-ietf`

**passwd**

+ 类型：*str*

+ 说明：ShadowsocksR连接密码

+ 缺省：必选

+ 可选值：不限

**protocol**

+ 类型：*str*

+ 说明：ShadowsocksR连接协议

+ 缺省：'origin'

+ 可选值：`origin`,`verify_sha1`,`verify_simple`,`verify_deflate`,`auth_simple`,`auth_sha1`,`auth_sha1_v2`,`auth_sha1_v4`,`auth_aes128`,`auth_aes128_md5`,`auth_aes128_sha1`,`auth_chain_a`,`auth_chain_b`,`auth_chain_c`,`auth_chain_d`,`auth_chain_e`,`auth_chain_f`

**protocolParam**

+ 类型：*str*

+ 说明：ShadowsocksR协议参数

+ 缺省：''

+ 可选值：不限

**obfs**

+ 类型：*str*

+ 说明：ShadowsocksR混淆方式

+ 缺省：'plain'

+ 可选值：`plain`,`http_post`,`http_simple`,`tls_simple`,`tls1.2_ticket_auth`,`tls1.2_ticket_fastauth`,`random_head`

**obfsParam**

+ 类型：*str*

+ 说明：ShadowsocksR混淆参数

+ 缺省：''

+ 可选值：不限
