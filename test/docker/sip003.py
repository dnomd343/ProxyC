#!/usr/bin/python
# -*- coding:utf-8 -*-

testHost = "dns.343.re"
testCert = "/etc/ssl/certs/dns.343.re/certificate.crt"
testKey = "/etc/ssl/certs/dns.343.re/private.key"

testGoQuiet = '''
{
  "key": "dnomd343"
}
'''

testCloak = '''
{
  "BypassUID": [
    "Q3iw2bAbC3KZvpm58XR6+Q=="
  ],
  "RedirAddr": "www.bing.com",
  "PrivateKey": "SFMUZ2g7e0jqzXXhBh5/rh/Odslnyu8A3LuZqH4ySVM="
}
'''

testRabbitPort = 12345

plugin_cmds = [
    # simple-obfs
    {
        "server": '--plugin obfs-server --plugin-opts "obfs=http"',
        "client": '--plugin obfs-local --plugin-opts "obfs=http;obfs-host=www.bing.com"',
    },
    {
        "server": '--plugin obfs-server --plugin-opts "obfs=tls"',
        "client": '--plugin obfs-local --plugin-opts "obfs=tls;obfs-host=www.bing.com"',
    },
    {
        "server": '--plugin obfs-server --plugin-opts "obfs=http"',
        "client": '--plugin obfs-local --plugin-opts "obfs=http;http-method=POST;obfs-host=www.bing.com"',
    },
    {
        "server": '--plugin obfs-server --plugin-opts "obfs=http"',
        "client": '--plugin obfs-local --plugin-opts "obfs=http;obfs-host=www.bing.com;obfs-uri=/test"',
    },
    # simple-tls
    {
        "server": '--plugin simple-tls --plugin-opts "s;n=$HOST"',
        "client": '--plugin simple-tls --plugin-opts "n=$HOST;no-verify"',
    },
    {
        "server": '--plugin simple-tls --plugin-opts "s;n=$HOST;auth=dnomd343"',
        "client": '--plugin simple-tls --plugin-opts "n=$HOST;no-verify;auth=dnomd343"',
    },
    {
        "server": '--plugin simple-tls --plugin-opts "s;n=$HOST;ws;ws-path=/test"',
        "client": '--plugin simple-tls --plugin-opts "n=$HOST;no-verify;ws;ws-path=/test"',
    },
    # v2ray-plugin
    {
        "server": '--plugin v2ray-plugin --plugin-opts "server"',
        "client": '--plugin v2ray-plugin',
    },
    {
        "server": '--plugin v2ray-plugin --plugin-opts "server;path=/test"',
        "client": '--plugin v2ray-plugin --plugin-opts "path=/test"',
    },
    {
        "server": '--plugin v2ray-plugin --plugin-opts "server;tls;host=$HOST;cert=$CERT;key=$KEY"',
        "client": '--plugin v2ray-plugin --plugin-opts "tls;host=$HOST"',
    },
    {
        "server": '--plugin v2ray-plugin --plugin-opts "server;mode=quic;host=$HOST;cert=$CERT;key=$KEY"',
        "client": '--plugin v2ray-plugin --plugin-opts "mode=quic;host=$HOST"',
    },
    # xray-plugin
    {
        "server": '--plugin xray-plugin --plugin-opts "server"',
        "client": '--plugin xray-plugin',
    },
    {
        "server": '--plugin xray-plugin --plugin-opts "server;tls;host=$HOST;cert=$CERT;key=$KEY"',
        "client": '--plugin xray-plugin --plugin-opts "tls;host=$HOST"',
    },
    {
        "server": '--plugin xray-plugin --plugin-opts "server;mode=quic;host=$HOST;cert=$CERT;key=$KEY"',
        "client": '--plugin xray-plugin --plugin-opts "mode=quic;host=$HOST"',
    },
    {
        "server": '--plugin xray-plugin --plugin-opts "server;mode=grpc;host=$HOST;cert=$CERT;key=$KEY"',
        "client": '--plugin xray-plugin --plugin-opts "mode=grpc"',
    },
    {
        "server": '--plugin xray-plugin --plugin-opts "server;tls;mode=grpc;host=$HOST;cert=$CERT;key=$KEY"',
        "client": '--plugin xray-plugin --plugin-opts "tls;mode=grpc;host=$HOST"',
    },
    # kcptun
    {
        "server": '--plugin kcptun-server',
        "client": '--plugin kcptun-client',
    },
    {
        "server": '--plugin kcptun-server --plugin-opts "nocomp"',
        "client": '--plugin kcptun-client --plugin-opts "nocomp"',
    },
    {
        "server": '--plugin kcptun-server --plugin-opts "key=dnomd343"',
        "client": '--plugin kcptun-client --plugin-opts "key=dnomd343"',
    },
    {
        "server": '--plugin kcptun-server --plugin-opts "crypt=twofish;mode=fast3"',
        "client": '--plugin kcptun-client --plugin-opts "crypt=twofish;mode=fast3"',
    },
    # gost-plugin
    {
        "server": '--plugin gost-plugin --plugin-opts "server;mode=ws"',
        "client": '--plugin gost-plugin --plugin-opts "mode=ws"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;mode=mws"',
        "client": '--plugin gost-plugin --plugin-opts "mode=mws;mux=1"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=tls"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=tls"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=xtls"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=xtls"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=mtls"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=mtls;mux=1"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=h2"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=h2"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=wss"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=wss"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=mwss"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=mwss;mux=1"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=quic"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=quic"',
    },
    {
        "server": '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=grpc"',
        "client": '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=grpc"',
    },
    # Cloak
    {
        "server": '--plugin ck-server --plugin-opts "/tmp/Cloak.json"',
        "client": '--plugin ck-client --plugin-opts "UID=Q3iw2bAbC3KZvpm58XR6+Q==;PublicKey=xTbqKW4Sg/xjDXDhys26ChXUQSrgxO+mBflTUeQpfWQ=;ServerName=www.bing.com;BrowserSig=chrome;NumConn=4;EncryptionMethod=plain;StreamTimeout=300"',
    },
    # GoQuiet
    {
        "server": '--plugin gq-server --plugin-opts "/tmp/GoQuiet.json"',
        "client": '--plugin gq-client --plugin-opts "ServerName=www.bing.com;key=dnomd343;TicketTimeHint=300;Browser=chrome"',
    },
    # mos-tls-tunnel
    {
        "server": '--plugin mtt-server --plugin-opts "cert=$CERT;key=$KEY"',
        "client": '--plugin mtt-client --plugin-opts "n=$HOST"',
    },
    {
        "server": '--plugin mtt-server --plugin-opts "wss;cert=$CERT;key=$KEY"',
        "client": '--plugin mtt-client --plugin-opts "wss;n=$HOST"',
    },
    {
        "server": '--plugin mtt-server --plugin-opts "wss;wss-path=/test;cert=$CERT;key=$KEY"',
        "client": '--plugin mtt-client --plugin-opts "wss;wss-path=/test;n=$HOST"',
    },
    # qtun
    {
        "server": '--plugin qtun-server --plugin-opts "cert=$CERT;key=$KEY"',
        "client": '--plugin qtun-client --plugin-opts "host=$HOST"',
    },
    # gun-plugin
    {
        "server": '--plugin gun-plugin --plugin-opts "server:cleartext"',
        "client": '--plugin gun-plugin --plugin-opts "client:cleartext"',
    },
    {
        "server": '--plugin gun-plugin --plugin-opts "server:$CERT:$KEY"',
        "client": '--plugin gun-plugin --plugin-opts "client:$HOST"',
    },
]

shadowsocks_cmds = [
    {
        "server": "ss-bootstrap-server --shadowsocks ss-python-server --no-udp -s 0.0.0.0 -p $SERVER_PORT -k dnomd343 -m aes-256-ctr",
        "client": "ss-bootstrap-local --shadowsocks ss-python-local --no-udp -s 127.0.0.1 -p $SERVER_PORT -b 0.0.0.0 -l $LOCAL_PORT -k dnomd343 -m aes-256-ctr",
        "killFlag": "ss-bootstrap-",
        "name": "ss-python"
    },
    {
        "server": "ss-bootstrap-server --shadowsocks ss-python-legacy-server --no-udp -s 0.0.0.0 -p $SERVER_PORT -k dnomd343 -m aes-256-ctr",
        "client": "ss-bootstrap-local --shadowsocks ss-python-legacy-local --no-udp -s 127.0.0.1 -p $SERVER_PORT -b 0.0.0.0 -l $LOCAL_PORT -k dnomd343 -m aes-256-ctr",
        "killFlag": "ss-bootstrap-",
        "name": "ss-python-legacy"
    },
    {
        "server": "ss-libev-server -s 0.0.0.0 -p $SERVER_PORT -k dnomd343 -m aes-256-ctr",
        "client": "ss-libev-local -s 127.0.0.1 -p $SERVER_PORT -b 0.0.0.0 -l $LOCAL_PORT -k dnomd343 -m aes-256-ctr",
        "killFlag": "ss-libev-",
        "name": "ss-libev"
    },
    {
        "server": "ss-libev-legacy-server -s 0.0.0.0 -p $SERVER_PORT -k dnomd343 -m aes-256-ctr",
        "client": "ss-libev-legacy-local -s 127.0.0.1 -p $SERVER_PORT -b 0.0.0.0 -l $LOCAL_PORT -k dnomd343 -m aes-256-ctr",
        "killFlag": "ss-libev-legacy-",
        "name": "ss-libev-legacy"
    },
    {
        "server": "ss-rust-server -s 0.0.0.0:$SERVER_PORT -k dnomd343 -m aes-256-gcm",
        "client": "ss-rust-local -s 127.0.0.1:$SERVER_PORT -b 0.0.0.0:$LOCAL_PORT -k dnomd343 -m aes-256-gcm",
        "killFlag": "ss-rust-",
        "name": "ss-rust"
    }
]

command_list = []

server_port_start = 20001
client_port_start = 10001

server_port = server_port_start
client_port = client_port_start

command_list.append("cat>/tmp/Cloak.json<<EOF")
command_list.append(testCloak.strip())
command_list.append("EOF")
command_list.append("cat>/tmp/GoQuiet.json<<EOF")
command_list.append(testGoQuiet.strip())
command_list.append("EOF")

# SIP003 plugin test
for ssType in shadowsocks_cmds:
    server_port_start = server_port
    client_port_start = client_port
    command_list.append('echo -n "Start ' + ssType['name'] + ' servers and clients..."')
    for pluginType in plugin_cmds:
        command_list.append((ssType['server'] + " " + pluginType['server']).replace("$SERVER_PORT", str(server_port)) + " > /dev/null 2>&1 &")
        command_list.append((ssType['client'] + " " + pluginType['client']).replace("$SERVER_PORT", str(server_port)).replace("$LOCAL_PORT", str(client_port)) + " > /dev/null 2>&1 &")
        server_port += 1
        client_port += 1
    command_list.append('sleep 8 && echo "OK"')
    for port in range(client_port_start, client_port):
        command_list.append('echo -n "' + str(port) + ' -> " && curl ip.343.re --socks5 127.0.0.1:' + str(port))
    command_list.append("kill `ps aux | grep " + ssType['killFlag'] + " | grep -v grep | awk '{print $1}'`")
    command_list.append('sleep 1')
command_list.append("rm -f /tmp/Cloak.json")
command_list.append("rm -f /tmp/GoQuiet.json")

# Rabbit test (no server plugin)
command_list.append('echo -n "Start the rabbit..."')
command_list.append("rabbit -mode s -password dnomd343 -rabbit-addr :" + str(testRabbitPort) + " > /dev/null 2>&1 &")
server_port_start = server_port
client_port_start = client_port
for ssType in shadowsocks_cmds:
    command_list.append(ssType['server'].replace("$SERVER_PORT", str(server_port)) + " > /dev/null 2>&1 &")
    command_list.append(ssType['client'].replace("$SERVER_PORT", str(testRabbitPort)).replace("$LOCAL_PORT", str(client_port)) + ' --plugin rabbit-plugin --plugin-opts "serviceAddr=127.0.0.1:' + str(server_port) + ';password=dnomd343" > /dev/null 2>&1 &')
    server_port += 1
    client_port += 1
command_list.append('sleep 3 && echo "OK"')
for port in range(client_port_start, client_port):
    command_list.append('echo -n "' + str(port) + ' -> " && curl ip.343.re --socks5 127.0.0.1:' + str(port))
command_list.append("kill `ps aux | grep ss- | grep -v grep | awk '{print $1}'`")
command_list.append("kill `ps aux | grep rabbit | grep -v grep | awk '{print $1}'`")
command_list.append('echo "Done"')

# Output
for cmd in command_list:
    cmd = cmd.replace("$HOST", testHost).replace("$CERT", testCert).replace("$KEY", testKey)
    print(cmd)
