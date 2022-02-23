import ProxyFilter as Filter

info = {
    'type': 'vmess',
    'remark': None,
    'server': b'127.0.0.1',
    'port': b"12345",
    'method': 'aes-128_gcm',
    'id': 'eb6273f1-a98f-59f6-ba52-945f11dee100',
    'stream': {
        'type': 'grpc',
        'service': 'test',
        'secure': {}
    }
}

status, data = Filter.filte(info, isExtra = True)
print(status)
print(data)
