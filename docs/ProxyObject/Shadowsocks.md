## ssObject

```
{
    'server': ---,
    'port': ---,
    'method': ---,
    'passwd': ---,
    'plugin': ---,
}
```

### server

+ 类型：*str*
+ 说明：Shadowsocks服务地址
+ 缺省：必选
+ 限制：IP地址或域名

### port

+ 类型：*int*
+ 说明：Shadowsocks服务端口
+ 缺省：必选
+ 限制：1 ～ 65535

### method

+ 类型：*str*
+ 说明：Shadowsocks加密方式
+ 缺省：必选
+ 限制：（以下69种加密方式）

`aes-128-ccm`, `aes-256-ccm`

`aes-128-gcm-siv`, `aes-256-gcm-siv`

`aes-128-gcm`, `aes-192-gcm`, `aes-256-gcm`

`aes-128-ctr`, `aes-192-ctr`, `aes-256-ctr`

`aes-128-ocb`, `aes-192-ocb`, `aes-256-ocb`

`aes-128-ofb`, `aes-192-ofb`, `aes-256-ofb`

`aes-128-cfb`, `aes-192-cfb`, `aes-256-cfb`

`aes-128-cfb1`, `aes-192-cfb1`, `aes-256-cfb1`

`aes-128-cfb8`, `aes-192-cfb8`, `aes-256-cfb8`

`aes-128-cfb128`, `aes-192-cfb128`, `aes-256-cfb128`

`camellia-128-ctr`, `camellia-192-ctr`, `camellia-256-ctr`

`camellia-128-ofb`, `camellia-192-ofb`, `camellia-256-ofb`

`camellia-128-cfb`, `camellia-192-cfb`, `camellia-256-cfb`

`camellia-128-cfb1`, `camellia-192-cfb1`, `camellia-256-cfb1`

`camellia-128-cfb8`, `camellia-192-cfb8`, `camellia-256-cfb8`

`camellia-128-cfb128`, `camellia-192-cfb128`, `camellia-256-cfb128`

`none`, `plain`, `table`, `rc4`, `rc4-md5`

`bf-cfb`, `des-cfb`, `rc2-cfb`, `idea-cfb`, `seed-cfb`, `cast5-cfb`

`salsa20`, `chacha20`, `xchacha20`, `salsa20-ctr`, `chacha20-ietf`

`chacha20-poly1305`, `chacha20-ietf-poly1305`, `xchacha20-ietf-poly1305`

`2022-blake3-aes-128-gcm`, `2022-blake3-aes-256-gcm`

`2022-blake3-chacha8-poly1305`, `2022-blake3-chacha20-poly1305`

### passwd

+ 类型：*str*
+ 说明：Shadowsocks连接密码
+ 缺省：必选
+ 限制：无

### plugin

+ 类型：*None* / [*pluginObject*](#pluginobject)
+ 说明：SIP003插件选项
+ 缺省：`None`
+ 限制：无

## pluginObject

```
{
    'type': ---,
    'param': ---,
}
```

### type

+ 类型：*str*
+ 说明：插件名称
+ 缺省：必选
+ 限制：（以下12种插件名称）

`obfs-local`, `simple-tls`

`kcptun-client`, `qtun-client`, `gun-plugin`

`v2ray-plugin`, `xray-plugin`, `gost-plugin`

`ck-client`, `gq-client`, `mtt-client`, `rabbit-plugin`

### param

+ 类型：*str*
+ 说明：插件参数
+ 缺省：`空`
+ 限制：无
