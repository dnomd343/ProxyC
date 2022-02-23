import ProxyFilter as Filter

info = {
    'type': 'vmess',
    'remark': 'ok',
    'server': b'127.0.0.1 ',
    'port': b"12345",
    'method': 'aes-128_gcm',
    'id': 'eb6273f1-a98f-59f6-ba52-945f11dee100',
    'aid': '64',
    'stream': {
        'type': 'tcp',
        'obfs': {
            'host': '343.re',
            'path': '/test'
        },
        'secure': {}
    }
    # 'stream': {
    #     'type': 'grpc',
    #     'service': 'test',
    #     'secure': {
    #         'sni': 'ip.343.re',
    #         'verify': False
    #     }
    # }
}

status, data = Filter.filte(info, isExtra = True)
print(status)
print(data)
