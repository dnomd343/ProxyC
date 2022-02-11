import redis

redisPrefix = 'proxyc-'
redisHost = 'localhost'
redisPort = 6379

ssInfo = '{"tag": "f43c9bae21ae8693", "check": ["http"], "info": {"type": "ss", "server": "127.0.0.1", "port": 12345, "password": "dnomd343", "method": "aes-256-ctr", "plugin": "", "pluginParam": ""}}'
ssrInfo = '{"tag": "54cd9ba3a8e86f93", "check": ["http"], "info": {"type": "ssr", "server": "127.0.0.1", "port": 23456, "password": "dnomd343", "method": "table", "protocol": "auth_aes128_md5", "protocolParam": "", "obfs": "tls1.2_ticket_auth", "obfsParam": ""}}'
redisObject = redis.StrictRedis(host = redisHost, port = redisPort, db = 0)
redisObject.set(redisPrefix + 'check-a-f43c9bae21ae8693', ssInfo)
redisObject.set(redisPrefix + 'check-c-54cd9ba3a8e86f93', ssrInfo)
