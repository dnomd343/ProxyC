#!/usr/bin/python
# -*- coding:utf-8 -*-

method_list = {
    "ss-python": [
        "aes-128-gcm",
        "aes-192-gcm",
        "aes-256-gcm",
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-ocb",
        "aes-192-ocb",
        "aes-256-ocb",
        "aes-128-ofb",
        "aes-192-ofb",
        "aes-256-ofb",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "aes-128-cfb1",
        "aes-192-cfb1",
        "aes-256-cfb1",
        "aes-128-cfb8",
        "aes-192-cfb8",
        "aes-256-cfb8",
        "aes-128-cfb128",
        "aes-192-cfb128",
        "aes-256-cfb128",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "camellia-128-cfb128",
        "camellia-192-cfb128",
        "camellia-256-cfb128",
        "table",
        "rc4",
        "rc4-md5",
        "rc2-cfb",
        "bf-cfb",
        "cast5-cfb",
        "des-cfb",
        "idea-cfb",
        "seed-cfb",
        "salsa20",
        "xchacha20",
        "chacha20",
        "chacha20-ietf",
        "chacha20-poly1305",
        "chacha20-ietf-poly1305",
        "xchacha20-ietf-poly1305",
    ],
    "ss-python-legacy": [
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-ofb",
        "aes-192-ofb",
        "aes-256-ofb",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "aes-128-cfb1",
        "aes-192-cfb1",
        "aes-256-cfb1",
        "aes-128-cfb8",
        "aes-192-cfb8",
        "aes-256-cfb8",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "table",
        "rc4",
        "rc4-md5",
        "rc2-cfb",
        "bf-cfb",
        "cast5-cfb",
        "des-cfb",
        "idea-cfb",
        "seed-cfb",
        "salsa20",
        "salsa20-ctr",
        "chacha20",
    ],
    "ss-libev": [
        "aes-128-gcm",
        "aes-192-gcm",
        "aes-256-gcm",
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "rc4",
        "rc4-md5",
        "bf-cfb",
        "salsa20",
        "chacha20",
        "chacha20-ietf",
        "chacha20-ietf-poly1305",
        "xchacha20-ietf-poly1305",
    ],
    "ss-libev-legacy": [
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "table",
        "rc4",
        "rc4-md5",
        "rc2-cfb",
        "bf-cfb",
        "cast5-cfb",
        "des-cfb",
        "idea-cfb",
        "seed-cfb",
        "salsa20",
        "chacha20",
        "chacha20-ietf",
    ],
    "ss-rust": [
        "aes-128-gcm",
        "aes-256-gcm",
        "plain",
        "none",
        "chacha20-ietf-poly1305",
    ]
}

import sys

client_port_start = 10001
server_port_start = 20001
password = "dnomd343"

def type_to_filename(type):
    if type == "ss-python" or type == "ss-python-legacy":
        return "ss-bootstrap-"
    elif type == "ss-libev" or type == "ss-libev-legacy" or type == "ss-rust":
        return type + "-"
    else:
        return None

def gen_server_cmd(type, method, port):
    if type == "ss-python":
        if method == "aes-128-cfb128" or method == "aes-192-cfb128" or method == "aes-256-cfb128":
            method = "mbedtls:" + method
        if method == "camellia-128-cfb128" or method == "camellia-192-cfb128" or method == "camellia-256-cfb128":
            method = "mbedtls:" + method
        cmd = type_to_filename(type) + "server --shadowsocks ss-python-server"
        cmd += " -p " + port + " -k " + password + " -m " + method
        if method == "idea-cfb" or method == "seed-cfb":
            cmd += " --libopenssl=libcrypto.so.1.0.0"
    elif type == "ss-python-legacy":
        cmd = type_to_filename(type) + "server --shadowsocks ss-python-legacy-server"
        cmd += " -p " + port + " -k " + password + " -m " + method
    elif type == "ss-libev" or type == "ss-libev-legacy":
        cmd = type_to_filename(type) + "server -u -p " + port + " -k " + password + " -m " + method
    elif type == "ss-rust":
        cmd = type_to_filename(type) + "server -U -s 0.0.0.0:" + port + " -k " + password + " -m " + method
    else:
        print("unknow server type")
        sys.exit(1)
    return cmd + " > /dev/null 2>&1 &"

def gen_client_cmd(type, method, target_port, local_port):
    if type == "ss-python":
        if method == "aes-128-cfb128" or method == "aes-192-cfb128" or method == "aes-256-cfb128":
            method = "mbedtls:" + method
        if method == "camellia-128-cfb128" or method == "camellia-192-cfb128" or method == "camellia-256-cfb128":
            method = "mbedtls:" + method
        cmd = type_to_filename(type) + "local --shadowsocks ss-python-local"
        cmd += " -l " + local_port + " -s 127.0.0.1 -p " + target_port + " -k " + password + " -m " + method
        if method == "idea-cfb" or method == "seed-cfb":
            cmd += " --libopenssl=libcrypto.so.1.0.0"
    elif type == "ss-python-legacy":
        cmd = type_to_filename(type) + "local --shadowsocks ss-python-legacy-local"
        cmd += " -l " + local_port + " -s 127.0.0.1 -p " + target_port + " -k " + password + " -m " + method
    elif type == "ss-libev" or type == "ss-libev-legacy":
        cmd = type_to_filename(type) + "local -l " + local_port + " -s 127.0.0.1 -p " + target_port + " -k " + password + " -m " + method
    elif type == "ss-rust":
        cmd = type_to_filename(type) + "local -b 127.0.0.1:" + local_port + " -s 127.0.0.1:" + target_port + " -k " + password + " -m " + method
    else:
        print("unknow client type")
        sys.exit(1)
    return cmd + " > /dev/null 2>&1 &"

command_list = []
method_port_list = {}
client_port = client_port_start
server_port = server_port_start

# Server
command_list.append('echo -n "Start the servers..."')
for (type, methods) in method_list.items():
    for method in methods:
        if not method in method_port_list:
            method_port_list[method] = []
        method_port_list[method].append(server_port)
        command_list.append(gen_server_cmd(type, method, str(server_port)))
        server_port += 1
command_list.append('sleep 5 && echo "OK"')

# Client
for (type, methods) in method_list.items():
    command_list.append('echo -n "Start the ' + type + ' clients..."')
    for method in methods:
        for server_port in method_port_list[method]:
            command_list.append(gen_client_cmd(type, method, str(server_port), str(client_port)))
            client_port += 1
    command_list.append('sleep 5 && echo "OK"')
    # Curl test
    for port in range(client_port_start, client_port):
        command_list.append('echo -n "' + str(port) + ' -> " && curl ip.343.re --socks5 127.0.0.1:' + str(port))
    client_port_start = client_port
    command_list.append("kill `ps aux | grep " + type_to_filename(type) + "local | grep -v grep | awk '{print $1}'`")
    command_list.append('sleep 1')
command_list.append("kill `ps aux | grep ss-bootstrap-server | grep -v grep | awk '{print $1}'`")
command_list.append("kill `ps aux | grep ss-libev-server | grep -v grep | awk '{print $1}'`")
command_list.append("kill `ps aux | grep ss-libev-legacy-server | grep -v grep | awk '{print $1}'`")
command_list.append("kill `ps aux | grep ss-rust-server | grep -v grep | awk '{print $1}'`")
command_list.append('echo "Done"')

# Output
for cmd in command_list:
    print(cmd)
