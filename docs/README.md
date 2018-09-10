## 原理

1. 规划数据的接收方式，根据交易所而不同，一般是全部用websocket，但是一些交易所
需要使用定时任务，定时用REST取得数据

2. 取得的数据要经过一些简单处理，简化字段为小写，统一一些字段名

3. 取得的数据先存放在内存(tunnels)中，然后用bulk insert写入数据库(storage)，这样操作对数据库的负载
要求比较低

4. 每天会定时把数据库的数据备份(backup)

## 项目结构

- `sdk`目录代表各个交易所的REST，Websocket连接程序
- `schemas`数据的格式化class等
- `backup`数据的备份，目前只有s3
- `storage`数据的存储，目前只有mongo
- `tunnels`数据的临时中转，目前只用python内置的Queue
- `monitors`数据接收-处理-存储的规划

## 数据表字段

- 细节需要查看各个交易所的文档
- 每个数据表都有一个`created`，代表本地创建数据的时间
- 一些字段为了nomarlize，做了统一化命名:
    - trades数据的交易单id，统一为`tid`
    - trades数据的交易方向，统一为`direction`
    - kline数据的起始时间，统一为`start_time`