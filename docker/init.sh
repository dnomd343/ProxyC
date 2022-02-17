python /usr/local/share/ProxyC/docker/compile.py&
/usr/bin/redis-server /etc/redis.conf

dnsproxy -p 53 -u 223.5.5.5 &
echo "nameserver 127.0.0.1" > /etc/resolv.conf

python /usr/local/share/ProxyC/Loop.py&
python /usr/local/share/ProxyC/Web.py
