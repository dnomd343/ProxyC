import ProxyFilter as Filter

info = {
    'type': 'ss',
    'remark': 'ok',
    'server': b'127.0.0.1 ',
    'port': b"12345",
    'method': 'aes-128_gcm',
    'passwd': 'dnomd343',
    'protocol': 'auth_chain-a',
    'protocolParam': '123',
    # 'obfs': b"http-simple",
    'obfsParam': b'123',
    'plugin': {
        'type': 'OBFS_server',
        'param': 'obfs=tls'
    }
}

status, data = Filter.filte(info, isExtra = True)
print(status)
print(data)
