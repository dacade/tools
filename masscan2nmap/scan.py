import get_title
import os
import nmap
import json
from queue import Queue
# 线程池经测试会GG，特采用Process方式
from multiprocessing import Process, Lock
import time
from rich.console import Console
console = Console()

dt = time.strftime('%Y-%m-%d %H:%M:%S')
# 创建进程互斥锁
lock = Lock()
task_queue = Queue()
services_info = []


# 调用masscan
def port_scan():
    ip_port = []
    dataList = {}
    console.print('./masscan/bin/masscan -iL ip.txt -p 1-65535 -oJ masscan.json --rate 2000',style="#ADFF2F")
    os.system('./masscan/bin/masscan -iL ip.txt -p 1-65535 -oJ masscan.json --rate 2000')
    if os.path.exists('masscan.json'):
    # 提取json文件中的端口
        with open('masscan.json', 'r') as f:
            for line in f:
                if line.startswith('{ '):
                    temp = json.loads(line)
                    temp1 = temp["ports"][0]
                    ip_port.append(temp["ip"] + '|' + str(temp1["port"]))

        if os.path.exists('masscan.json'):
            os.remove('masscan.json')
        else:
            pass
    else:
        console.print("[-]masscan扫描未发现端口开放")

    # 添加一个端口过滤的功能
    for i in ip_port:
        i = i.split('|')
        if i[0] not in dataList:
            dataList[str(i[0])] = []
        dataList[str(i[0])].append(i[1])
    for i in dataList:
        # 删除超过100个端口的
        if len(dataList[i]) >= 300:
            for port in dataList[i]:
                ip_port.remove(str(i) + '|' + str(port))
            with open('ip_waf.txt','a') as ff:
                ff.write(str(i)+'\n')
                ff.write('\n'+f'-------------------------------------------  {dt} -------------------------------------------'+'\n'+'\n')
    # 此处的ip_port已经实现了端口过滤功能
    # 放入队列，方便后续多进程处理
    for i in ip_port:
        task_queue.put(i)


def service_scan(ip_port):
    scan_ip_port = ip_port.split('|')
    ip = scan_ip_port[0]
    port = scan_ip_port[1]
    try:
        nm = nmap.PortScanner()
        ret = nm.scan(ip, port, arguments='-Pn -sSV')
        service_name = ret['scan'][ip]['tcp'][int(port)]['name']
        service_product = ret['scan'][ip]['tcp'][int(port)]['product']
        service_version = ret['scan'][ip]['tcp'][int(port)]['version']
        product_version = service_product + ' ' + service_version
        mess=f'[*]主机： {ip.ljust(20)} 端口:  {str(port).ljust(10)}  网络类型为：{service_name.ljust(15)}   产品以及版本为： {product_version.ljust(30)}'
        print(mess)

        lock.acquire()
        with open('url_title.txt', 'a') as f2:
            f2.write(mess + '\n')
        lock.release()

        if 'http' in service_name or service_name == 'sun-answerbook':
            if 'https' in service_name:
                scan_url_port = f'https://{ip}:{str(port)}'
            else:
                scan_url_port = f'http://{ip}:{str(port)}'
        else:
            scan_url_port = f'http://{ip}:{str(port)}'
        lock.acquire()
        with open('url.txt', 'a') as f:
            f.write(scan_url_port + '\n')
        lock.release()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    # 防止上次结果造成干扰
    if os.path.exists('paused.conf'):
        os.remove('paused.conf')
    else:
        pass

    port_scan()
    console.print('[+]端口扫描完毕，即将进行服务识别...',style="#ADFF2F")
    process_list = []
    while not task_queue.empty():
        # 修改进程数请在此处修改range(10)
        for i in range(10):
            try:
                ip_port = task_queue.get(timeout=10)
                p = Process(target=service_scan, args=(ip_port,))
                p.start()
                process_list.append(p)
            except:
                pass
        for j in process_list:
            j.join()
        process_list.clear()

    if os.path.exists('url.txt'):
        console.print('[+]即将开始进行title获取...',style="#ADFF2F")
        get_title.get_title()
        os.remove('url.txt')
    else:
        pass

    if os.path.exists('paused.conf'):
        os.remove('paused.conf')
    else:
        pass
