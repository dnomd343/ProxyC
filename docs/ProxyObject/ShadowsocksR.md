## ssrObject

```
{
    'server': ---,
    'port': ---,
    'method': ---,
    'passwd': ---,
    'protocol': ---,
    'protocolParam': ---,
    'obfs': ---,
    'obfsParam': ---,
}
```

### server

+ 类型：*str*
+ 说明：ShadowsocksR服务地址
+ 缺省：必选
+ 限制：IP地址或域名

### port

+ 类型：*int*
+ 说明：ShadowsocksR服务端口
+ 缺省：必选
+ 限制：1 ～ 65535

### method

+ 类型：*str*
+ 说明：ShadowsocksR加密方式
+ 缺省：必选
+ 限制：（以下37种加密方式）

`none`, `table`

`rc4`, `rc4-md5`, `rc4-md5-6`

`bf-cfb`, `cast5-cfb`, `des-cfb`

`idea-cfb`, `seed-cfb`, `rc2-cfb`

`aes-128-gcm`, `aes-192-gcm`, `aes-256-gcm`

`aes-128-ctr`, `aes-192-ctr`, `aes-256-ctr`

`aes-128-ofb`, `aes-192-ofb`, `aes-256-ofb`

`aes-128-cfb`, `aes-192-cfb`, `aes-256-cfb`

`aes-128-cfb1`, `aes-192-cfb1`, `aes-256-cfb1`

`aes-128-cfb8`, `aes-192-cfb8`, `aes-256-cfb8`

`camellia-128-cfb`, `camellia-192-cfb`, `camellia-256-cfb`

`salsa20`, `xsalsa20`, `chacha20`, `xchacha20`, `chacha20-ietf`

### passwd

+ 类型：*str*
+ 说明：ShadowsocksR连接密码
+ 缺省：必选
+ 限制：无

### protocol

+ 类型：*str*
+ 说明：ShadowsocksR传输协议
+ 缺省：`origin`
+ 限制：（以下17种传输协议）

`origin`, `auth_simple`

`auth_sha1`, `auth_sha1_v2`, `auth_sha1_v4`

`auth_chain_a`, `auth_chain_b`, `auth_chain_c`

`auth_chain_d`, `auth_chain_e`, `auth_chain_f`

`auth_aes128`, `auth_aes128_md5`, `auth_aes128_sha1`

`verify_sha1`, `verify_simple`, `verify_deflate`

### protocolParam

+ 类型：*str*
+ 说明：ShadowsocksR协议参数
+ 缺省：`空`
+ 限制：无

### obfs

+ 类型：*str*
+ 说明：ShadowsocksR混淆方式
+ 缺省：`plain`
+ 限制：（以下7种混淆方式）

`plain`, `http_post`, `http_simple`, `random_head`

`tls_simple`, `tls1.2_ticket_auth`, `tls1.2_ticket_fastauth`

### obfsParam

+ 类型：*str*
+ 说明：ShadowsocksR混淆参数
+ 缺省：`空`
+ 限制：无
