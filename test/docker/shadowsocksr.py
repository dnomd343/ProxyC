#!/usr/bin/python
# -*- coding:utf-8 -*-

method_list = [
    "aes-128-cfb",
    "aes-192-cfb",
    "aes-256-cfb",
    "aes-128-cfb1",
    "aes-192-cfb1",
    "aes-256-cfb1",
    "aes-128-cfb8",
    "aes-192-cfb8",
    "aes-256-cfb8",
    "aes-128-ctr",
    "aes-192-ctr",
    "aes-256-ctr",
    "aes-128-gcm",
    "aes-192-gcm",
    "aes-256-gcm",
    "aes-128-ofb",
    "aes-192-ofb",
    "aes-256-ofb",
    "camellia-128-cfb",
    "camellia-192-cfb",
    "camellia-256-cfb",
    "none",
    "table",
    "rc4",
    "rc4-md5",
    "rc4-md5-6",
    "bf-cfb",
    "cast5-cfb",
    "des-cfb",
    "idea-cfb",
    "seed-cfb",
    "rc2-cfb",
    "salsa20",
    "xsalsa20",
    "chacha20",
    "xchacha20",
    "chacha20-ietf",
]

protocol_list = [
    "origin",
    "verify_sha1",
    "verify_simple",
    "verify_deflate",
    "auth_simple",
    "auth_sha1",
    "auth_sha1_v2",
    "auth_sha1_v4",
    "auth_aes128",
    "auth_aes128_md5",
    "auth_aes128_sha1",
    "auth_chain_a",
    "auth_chain_b",
    "auth_chain_c",
    "auth_chain_d",
    "auth_chain_e",
    "auth_chain_f",
]

obfs_list = [
    "plain",
    "http_post",
    "http_simple",
    "tls_simple",
    "tls1.2_ticket_auth",
    "tls1.2_ticket_fastauth",
    "random_head",
]

command_list = []

server_port_start = 20001
client_port_start = 10001

server_port = server_port_start
client_port = client_port_start

# methods test
command_list.append('echo -n "Start SSR servers and clients..."')
for method in method_list:
    command_list.append("ssr-server -s 0.0.0.0 -p " + str(server_port) + " -k dnomd343 -m " + method + " > /dev/null 2>&1 &")
    command_list.append("ssr-local -s 127.0.0.1 -p " + str(server_port) + " -b 0.0.0.0 -l " + str(client_port) + " -k dnomd343 -m " + method + " > /dev/null 2>&1 &")
    server_port += 1
    client_port += 1
command_list.append('sleep 8 && echo "OK"')
for port in range(client_port_start, client_port):
    command_list.append('echo -n "' + str(port) + ' -> " && curl ip.343.re --socks5 127.0.0.1:' + str(port))
command_list.append("kill `ps aux | grep ssr- | grep -v grep | awk '{print $1}'`")

# protocol and obfs
# for protocol in protocol_list:
for obfs in obfs_list:
    client_port_start = client_port
    command_list.append('echo -n "Start SSR servers and clients..."')
    # for obfs in obfs_list:
    for protocol in protocol_list:
        command_list.append("ssr-server -s 0.0.0.0 -p " + str(server_port) + " -k dnomd343 -m aes-256-ctr -O " + protocol + " -o " + obfs + " > /dev/null 2>&1 &")
        command_list.append("ssr-local -s 127.0.0.1 -p " + str(server_port) + " -b 0.0.0.0 -l " + str(client_port) + " -k dnomd343 -m aes-256-ctr -O " + protocol + " -o " + obfs + " > /dev/null 2>&1 &")
        server_port += 1
        client_port += 1
    command_list.append('sleep 5 && echo "OK"')
    for port in range(client_port_start, client_port):
        command_list.append('echo -n "' + str(port) + ' -> " && curl ip.343.re --socks5 127.0.0.1:' + str(port))
    command_list.append("kill `ps aux | grep ssr- | grep -v grep | awk '{print $1}'`")
    command_list.append('sleep 1')
command_list.append('echo "Done"')

for cmd in command_list:
    print(cmd)
