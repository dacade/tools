### **0x01 功能介绍**

masscan端口快速扫描+nmap服务精准识别，过滤含有防火墙的IP,协程获取http请求标题

![](https://github.com/dacade/tools/blob/master/masscan2nmap/1.png)

### **0x02 运行环境说明**

Linux + Python3

### **0x03 使用前准备**

**1.首先编译masscan**

- `apt install git gcc make libpcap-dev`
- `cd masscan`
- `make`

**2.安装python3依赖**

```
pip3 install -r requirements.txt
```

### **0x04 如何使用**

**1.在ip.txt中放入你要扫描的ip地址(masscan支持的ip格式)**

**例如：**

```
127.0.0.1
127.0.0.0/8
```

**2.启动扫描**

```
python3 scan.py
```

**3.在url_title.txt中查看扫描结果，在ip_waf中查看可能有waf而未进行端口扫描的ip**

注意，这个是追加写入的。

### **0x05 改动说明**

1.调解masscan速率到1000，防止丢失部分端口

2.其他优化【我也忘记了，反正是有的】

### 0x06 Thanks

https://github.com/7dog7/masscan_to_nmap
