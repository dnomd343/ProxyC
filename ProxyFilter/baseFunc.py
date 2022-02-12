import re
import IPy

def isHost(host: str) -> bool:
    '''
    判断host是否合法

    IPv4 / IPv6 / Domain

        合法: return True

        不合法: return False
    '''
    try:
        IPy.IP(host)
        if host.find('/') != -1: # filter CIDR
            return False
        return True
    except: # not IP address
        pass
    return (re.search(r'^(?=^.{3,255}$)[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62}(\.[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62})+$', host) != None)

def isPort(port) -> bool:
    '''
    判断端口是否合法

    1 ~ 65535

        合法: return True

        不合法: return False
    '''
    try:
        if isinstance(port, (int, str)):
            if int(port) >= 1 and int(port) <= 65535:
                return True
    except: # illegal
        pass
    return False
