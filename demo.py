import ProxyBuilder as Builder
import ProxyDecoder as Decoder
import ProxyFilter as Filter
import Check as Checker

info = {
    'type': 'trojan-go',
    'server': '127.0.0.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'sni': 'local.343.re',
    'plugin': {
        # 'type': 'obfs-local',
        # 'param': 'obfs=http;obfs-host=www.bing.com'
        'type': 'simple-tls',
        'param': 'n=local.343.re;no-verify'
    }
}

status, ret = Filter.filte(info, isExtra = True)
print(status)
print(ret)

data = Checker.proxyTest({
    'check': ['http'],
    'info': ret
})

print(data)
