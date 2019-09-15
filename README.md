# 操作系统安全加固

## 概述
根据CentOS配置规范以及公司环境需求, 编写操作系统安全加固脚本, 对新增主机进行基础软件安装和安全配置, 对已有主机进行配置检测并修复不规范配置.

## 功能需求
**新增虚拟机**
1. yum源代理配置
2. 软件安装
    + 基础环境: `vim`, `gcc`, `iftop`, `firewall-cmd`, `nslookup`, `iperf`, `telnet`, `zip`, `tar`, `lvm2`
    + 运行环境: `nginx`, `java`
    + 监控环境: `zabbix`
3. 服务项检测, 仅开启以下服务
    + ssh(tcp 22)
    + chronyd(udp 323)
4. 允许某些主机免密登录
5. 开启firewall-cmd  
    允许 ssh、zabbix-agent、chronyd(没有默认服务)
6. 进行操作系统规范配置

**已有的主机**
1. 配置检测功能
2. 修复不规范配置
3. 脚本要足够灵活

## 操作系统配置规范

### DNS配置规范
1. 配置主机解析顺序
    ```shell
    # /etc/host.conf
    order local,bind4
    ```
2. 允许一个主机对应多个IP
    ```shell
    # /etc/host.conf
    multi on
    ```
3. DNS服务器配置
    ```shell
    # 统一通过`nmcli`配置，centos后续版本会强制要求
    # 相关命令
    $ nmcli -version
    nmcli tool, version 1.12.0-10.el7_6
    # 查看连接
    $ nmcli connection show
    NAME         UUID   TYPE      DEVICE
    System eth0  12345  ethernet  eth0
    # 展示DNS
    $ nmcli dev show eth0 | grep IP4.DNS
    IP4.DNS[1]:                             *.*.*.*
    # 修改DNS
    $ nmcli connection modify 12345  ipv4.dns "*.*.*.* *.*.*.*"
    # 使生效, 之后查看/etc/resolv.conf文件, 可以看到nameserver已被自动修改
    $ nmcli connection up 12345
    Connection successfully activated (D-Bus active path: /org/freedesktop/NetworkManager/ActiveConnection/2)
    ```
4. 禁止SSH启用域名服务
    ```shell
    # /etc/ssh/sshd_config
    UseDNS no
    # 修改后需重启服务
    $ systemctl restart sshd
    ```
5. 开启DNS Cache功能
    ```shell
    $ yum -y install nscd
    $ systemctl start nscd
    $ systemctl enable nscdfi
    ```

### 系统时间配置
1. 系统时间同步  
    统一使用`chronyc`, 代替`ntpd`, 同时禁止使用`ntpupdate`  
    生产环境的内网中, 需要搭建一台内网时间服务器, 然后让其它计算机到服务端去同步
    ```shell
    # 安装
    $ yum -y install chrony
    
    # 启动 chronyd 服务
    $ systemctl enable chronyd
    $ systemctl start chronyd
   
    # 查看监听端口
    $ netstat -nlp | grep chronyd
    udp        0      0 127.0.0.1:323           0.0.0.0:*                           2570/chronyd
    udp6       0      0 ::1:323                 :::*                                2570/chronyd
    
    # 配置
    # 假设时间服务器IP是100.80.60.32
    # 服务端配置
    $ vim /etc/chrony.conf
    server 100.80.60.32 iburst # 表示与本机同步时间
    # 客户端配置
    $ vim /etc/chrony.conf
    server 100.80.60.32 iburst # 表示与时间服务器同步时间
    
    # 修改后需重启服务
    
    # 客户端chronyc相关命令
    # 查看时间同步源状态
    $ chronyc sources
    210 Number of sources = 4
    MS Name/IP address         Stratum Poll Reach LastRx Last sample               
    ===============================================================================
    ^? ntp.wdc1.us.leaseweb.net      2   6     1    84    -25ms[  -25ms] +/-  243ms
    ^+ undefined.hostname.local>     2   6   367    30    +12ms[  +12ms] +/-  133ms
    ^+ electabuzz.felixc.at          3   6   367    26    +25ms[  +25ms] +/-  158ms
    ^* ntp.xtom.nl                   2   6   377    27    -28ms[  -28ms] +/-  101ms
   
    $ chronyc sources -v
    210 Number of sources = 4
    
      .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
     / .- Source state '*' = current synced, '+' = combined , '-' = not combined,
    | /   '?' = unreachable, 'x' = time may be in error, '~' = time too variable.
    ||                                                 .- xxxx [ yyyy ] +/- zzzz
    ||      Reachability register (octal) -.           |  xxxx = adjusted offset,
    ||      Log2(Polling interval) --.      |          |  yyyy = measured offset,
    ||                                \     |          |  zzzz = estimated error.
    ||                                 |    |           \
    MS Name/IP address         Stratum Poll Reach LastRx Last sample               
    ===============================================================================
    ^? ntp.wdc1.us.leaseweb.net      2   7     2   187    -25ms[  -25ms] +/-  243ms
    ^+ undefined.hostname.local>     2   6   337     1    +15ms[  +15ms] +/-  136ms
    ^+ electabuzz.felixc.at          3   6   357    63    +25ms[  +25ms] +/-  159ms
    ^* ntp.xtom.nl                   2   6   375     1    -28ms[  -28ms] +/-  104ms
       
    $ chronyc activity
    200 OK
    4 sources online
    0 sources offline
    0 sources doing burst (return to online)
    0 sources doing burst (return to offline)
    0 sources with unknown address
    ```
2. 时区设置
    ```shell
    # 查看系统时间状态
    $ timedatectl status
          Local time: Tue 2019-09-10 19:12:06 CST
      Universal time: Tue 2019-09-10 11:12:06 UTC
            RTC time: Tue 2019-09-10 11:12:08
           Time zone: Asia/Shanghai (CST, +0800)
         NTP enabled: yes
    NTP synchronized: no
     RTC in local TZ: no
          DST active: n/a
    
    # 设置系统时区
    $ timedatectl set-timezone Asia/Shanghai
    
    # 设置完后，强制同步下时钟
    $ chronyc -a makestep
    200 OK
    ```

### 系统参数配置
1. 网络参数配置
    ```shell
    # /etc/sysctl.conf
    fs.file-max = 65536
    net.ipv4.ip_local_port_range = 1024 65500
    net.ipv4.tcp_tw_reuse = 1
    net.ipv4.tcp_tw_recycle = 0
    net.ipv4.tcp_keepalive_time = 600
    # 修改后执行以下命令, 是配置生效
    sysctl –p
    ```
2. 系统打开文件数
    ```shell
    # /etc/security/limits.conf
    *  -  nofile  65536
    ```
3. 系统连接数配置
    ```shell
    # /etc/security/limits.d/*-nproc.conf
    *          soft    nproc     5120
    root       soft    nproc     unlimited
    ```

### 账户口令
1. 空口令检测
    ```shell
    awk -F: '($2 == "") {printf("%s\n", $1)}' /etc/shadow
    ```
2. UID为0账号检测
    ```shell
    awk -F: '($3 == 0) {printf("%s\n", $1)}' /etc/shadow
    ```
3. 超时注销配置
    ```shell
    # /etc/profile
    export TMOUT=180
    ```
4. 限制root远程登录
    ```shell
    # /etc/securetty
    CONSOLE = /dev/tty01
    ```
5. 密码强度
    ```shell
    # /etc/login.defs
    PASS_MAX_DAYS 90 # 最大使用90天
    PASS_MIN_LEN  8  # 最小长度8位
    PASS_WARN_AGE 10 # 过期10天前警告
    ```

### 其它 
1. OpenSSH安全配置
    ```shell
    # /etc/ssh/sshd_config
    Protocol                2
    StrictModes             yes
    PermitRootLogin         no   # 不允许root远程登录
    PrintLastLog            yes  # SSH登录后打印上次登录日志
    PermitEmptyPasswords    no   # 不允许空密码
    # 修改后需重启sshd服务
    systemctl restart sshd
    ```
    ```
    PrintLastLog设为yes, 用户在SSH连接登录后, 终端可以看到如下日志
    Last login: Mon Sep  9 00:32:18 2019 from *.*.*.*
    ```
2. root路径检测
    ```shell
    # 环境变量path中不能包含当前目录':.'
    echo $PATH | grep ":\."
    ```
3. 保留历史命令数检测
    ```shell
    # /etc/profile
    HISTSIZE=5
    HISTFILESIZE=5
    ```
4. 磁盘剩余空间检测
    ```shell
    # 检测是否有磁盘使用率大于80%
    df -k | awk '(NR > 1 && $5 >= "80%"){printf("\033[31m%s\n\033[0m", $1)}'
    ```
5. 开启日志审核
    ```shell
    # /etc/rsyslog.conf
    authpriv.*        /var/log/secure
    ```

## 服务检测
```shell
# 端口及其服务检测
# 使用netstat命令
$ netstat -nlp -t -u
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:111             0.0.0.0:*               LISTEN      1/systemd
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      11121/sshd
tcp        0      0 127.0.0.1:45432         0.0.0.0:*               LISTEN      2042/postgres
tcp        0      0 127.0.0.1:25            0.0.0.0:*               LISTEN      2147/master
tcp        0      0 0.0.0.0:8834            0.0.0.0:*               LISTEN      2027/nessusd
tcp        0      0 0.0.0.0:13443           0.0.0.0:*               LISTEN      2341/opsrv
tcp6       0      0 :::111                  :::*                    LISTEN      1/systemd
tcp6       0      0 :::22                   :::*                    LISTEN      11121/sshd
tcp6       0      0 ::1:45432               :::*                    LISTEN      2042/postgres
tcp6       0      0 ::1:25                  :::*                    LISTEN      2147/master
tcp6       0      0 :::8834                 :::*                    LISTEN      2027/nessusd
udp        0      0 0.0.0.0:68              0.0.0.0:*                           31663/dhclient
udp        0      0 0.0.0.0:111             0.0.0.0:*                           1/systemd
udp        0      0 127.0.0.1:323           0.0.0.0:*                           6659/chronyd
udp        0      0 0.0.0.0:926             0.0.0.0:*                           7959/rpcbind
udp6       0      0 :::111                  :::*                                1/systemd
udp6       0      0 ::1:323                 :::*                                6659/chronyd
udp6       0      0 :::926                  :::*                                7959/rpcbind

# 使用nmap端口扫描工具
nmap -sT -sU -p1-65535 -O localhost

Starting Nmap 6.40 ( http://nmap.org ) at 2019-09-13 16:00 CST
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000028s latency).
Other addresses for localhost (not scanned): 127.0.0.1
Not shown: 131059 closed ports
PORT      STATE         SERVICE
22/tcp    open          ssh
25/tcp    open          smtp
111/tcp   open          rpcbind
4605/tcp  open          unknown
8834/tcp  open          unknown
13443/tcp open          unknown
45432/tcp open          unknown
68/udp    open|filtered dhcpc
111/udp   open          rpcbind
323/udp   open|filtered unknown
926/udp   open|filtered unknown
Device type: general purpose
Running: Linux 3.X
OS CPE: cpe:/o:linux:linux_kernel:3
OS details: Linux 3.7 - 3.9
Network Distance: 0 hops

OS detection performed. Please report any incorrect results at http://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 9.48 seconds
```

## firewall-cmd 命令
```shell
# 开启firewalld服务
$ systemctl start firewalld

# 允许服务通过
$ firewall-cmd --add-service=zabbix-agent --permanent
success

加上--permanent是永久生效, 不然firewall-cmd --reload之后, 改变无效

# 查看允许通过的服务
$ firewall-cmd --list-services
ssh dhcpv6-client zabbix-agent

# 禁止服务通过
$ firewall-cmd --remove-service=dhcpv6-client --permanent
success

# 查看默认服务
$ firewall-cmd --get-services
mysql redis ssh telnet zabbix-agent zabbix-server ...(没有chronyd)

$ firewall-cmd --add-service=chronyd --permanent
Error: INVALID_SERVICE: chronyd

# 自定义服务 
$ firewall-cmd --new-service=chronyd --permanent
success
$ firewall-cmd --service=chronyd --add-port=323/tcp --permanent
success
$ firewall-cmd --service=chronyd --add-port=323/udp --permanent
success
# 查询服务端口及协议
$ firewall-cmd --service=chronyd --get-ports --permanent
323/tcp 323/udp
# 重新加载, 不然服务仍会无效
$ firewall-cmd --reload
success
# 允许通过, 返回成功
firewall-cmd --add-service=chronyd --permanent
success
```
## 参考链接
1. [使用NetworkManager命令行工具NMCLI](https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/networking_guide/sec-using_the_networkmanager_command_line_tool_nmcli)
2. [Linux查看修改DNS配置](https://www.cnblogs.com/kerrycode/p/5407635.html)
3. [chronyc(1) Manual Page](https://chrony.tuxfamily.org/doc/3.1/chronyc.html)