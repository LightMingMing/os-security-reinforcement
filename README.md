# 操作系统安全加固

## 概述
根据CentOS配置规范以及公司环境需求, 编写操作系统安全加固脚本, 对新增主机进行基础软件安装和安全配置, 对已有主机进行配置检测并修复不规范配置.

## 功能需求
**新增虚拟机**
1. yum源代理配置
2. 软件安装
    + 基础环境: `vim`, `gcc`, `iftop`, `firewall-cmd`, `nslookup`, `iftop`, `iperf`, `telnet`, `zip`, `tar`, `lvm2`
    + 运行环境: `nginx`, `java`
    + 监控环境: `zabbix`
3. 服务项检测, 仅开启以下服务
    + ssh(tcp 22)
    + chronyd(udp 323)
4. 时区配置: 东八区
5. 允许某些主机免密登录
6. 开启firewall-cmd  
    允许 ssh、zabbix-agent、chronyd(没有默认服务)
7. 进行操作系统规范配置

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
    # TODO
    ```
4. 禁止SSH启用域名服务
    ```shell
    # /etc/ssh/sshd_config
    UseDNS no
    # 修改后需重启服务
    systemctl restart sshd
    ```
5. 开启DNS Cache功能
    ```shell
    yum -y install nscd
    systemctl start nscd
    systemctl enable nscdfi
    ```

### 系统时间配置
统一使用`chronyc`, 代替`ntpd`, 同时禁止使用`ntpupdate`
```shell
# TODO
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