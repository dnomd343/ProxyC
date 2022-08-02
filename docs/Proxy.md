# 代理节点格式

## Shadowsocks

```
{
    'type': 'ss',
    'name': '...',
    'info': ssObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [ssObject](./ProxyObject/Shadowsocks.md)：节点信息

## ShadowsocksR

```
{
    'type': 'ssr',
    'name': '...',
    'group': '...',
    'info': ssrObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ group：节点群组（可选）
+ [ShadowsocksR](./ProxyObject/ShadowsocksR.md)：节点信息

## VMess

```
{
    'type': 'vmess',
    'name': '...',
    'info': vmessObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [vmessObject](./ProxyObject/VMess.md)：节点信息

## VLESS

```
{
    'type': 'vless',
    'name': '...',
    'info': vlessObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [vlessObject](./ProxyObject/VLESS.md)：节点信息

## Trojan

```
{
    'type': 'trojan',
    'name': '...',
    'info': trojanObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [trojanObject](./ProxyObject/Trojan.md)：节点信息

## Trojan-Go

```
{
    'type': 'trojan-go',
    'name': '...',
    'info': trojanGoObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [trojanGoObject](./ProxyObject/TrojanGo.md)：节点信息

## Brook

```
{
    'type': 'brook',
    'name': '...',
    'info': brookObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [brookObject](./ProxyObject/Brook.md)：节点信息

## Hysteria

```
{
    'type': 'hysteria',
    'name': '...',
    'info': hysteriaObject
}
```

+ type：节点类型
+ name：节点名称（可选）
+ [hysteriaObject](./ProxyObject/Hysteria.md)：节点信息
