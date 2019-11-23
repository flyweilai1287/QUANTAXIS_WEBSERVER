# QUANTAXIS 的后台api

<!-- TOC -->

- [QUANTAXIS 的后台api](#quantaxis-的后台api)
    - [1. 后端的标准和格式规范](#1-后端的标准和格式规范)
        - [1.1. 基础标准](#11-基础标准)
    - [2. 命名格式](#2-命名格式)
    - [3. 后端的实现方式和注意事项](#3-后端的实现方式和注意事项)
        - [3.1. 跨域支持](#31-跨域支持)
            - [3.1.1. Flask](#311-flask)
            - [3.1.2. Tornado](#312-tornado)
            - [3.1.3. express](#313-express)
        - [3.2. 权限](#32-权限)
    - [4. 必须实现的部分](#4-必须实现的部分)
        - [4.1. 用户管理 /user](#41-用户管理-user)
            - [4.1.1.登陆](#411登陆)
            - [4.1.2. 注册](#412-注册)
        - [4.2. 回测部分 /backtest](#42-回测部分-backtest)
            - [4.2.1. 回测概览(列表查询)](#421-回测概览列表查询)
            - [4.2.2. 单个回测结果查询()](#422-单个回测结果查询)
        - [4.3. 行情查询部分 /marketdata & /data](#43-行情查询部分-marketdata--data)
            - [4.3.1. URI总规则 GENERAL URI RULE](#431-uri总规则-general-uri-rule)
            - [4.3.2. 股票日线 STOCK DAY](#432-股票日线-stock-day)
            - [4.3.3. 股票分钟线 STOCK MINDATA](#433-股票分钟线-stock-mindata)
            - [4.3.4. 股票实时上下五档 STOCK REALTIME PRICE 5-ASK/BID](#434-股票实时上下五档-stock-realtime-price-5-askbid)
            - [4.3.5. 股票分笔数据 STOCK TRANSACTION](#435-股票分笔数据-stock-transaction)
            - [4.3.6. 股票财务数据](#436-股票财务数据)
            - [4.3.7. 期货日线](#437-期货日线)
            - [4.3.8. 期货分钟线](#438-期货分钟线)
        - [4.4. 实时行情推送 /realtime](#44-实时行情推送-realtime)
        - [4.5 账户查询 /accounts](#45-账户查询-accounts)
            - [4.5.1 全部账户列表查询](#451-全部账户列表查询)
            - [4.5.2 单个账户查询](#452-单个账户查询)
        - [4.6 风险查询 /risks](#46-风险查询-risks)
        - [4.7 下单 /trade | /tradeinfo](#47-下单-trade--tradeinfo)
            - [4.7.1 静态信息查询](#471-静态信息查询)
            - [4.7.2 websocket接口](#472-websocket接口)

<!-- /TOC -->
<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->


quantaxis 采用前后端分离的模式开发,所以对于后端而言 是一个可以快速替换/语言随意的部分.只需要按照规则设置好REST的url即可


##  1. 后端的标准和格式规范

###  1.1. 基础标准

quantaxis的后台可以用 nodejs(express/koa), python(flask/django/tornado), go 等等语言实现

quantaxis的后台部分主要是作为微服务,给前端(web/client/app)等提供标准化的查询/交互接口


##  2. 命名格式

quantaxis的后台命名格式

http://ip:port/功能(backtest/marketdata/user/..)/细分功能(info/query_code/..)

example:

```
http://localhost:3000/backtest/info_cookie?cookie=xxxxx  ==>  按backtest的cookie查询backtest的信息

```

##  3. 后端的实现方式和注意事项


###  3.1. 跨域支持

因为是前后端分离的模式, 需要对于url采取跨域允许

跨域在python中的实现

####  3.1.1. Flask

```python
@app.route("/status")
def status():
    rst = make_response(jsonify('200'))
    rst.headers['Access-Control-Allow-Origin'] = '*'
    rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    rst.headers['Access-Control-Allow-Headers'] = allow_headers
    return rst
```


####  3.1.2. Tornado

```python
class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        print（"setting headers!!!"）
        self.set_header("Access-Control-Allow-Origin", "*") # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
	self.set_header('Server', 'QUANTAXISBACKEND')
    def post(self):
        self.write('some post')

    def get(self):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()
```

跨域在nodejs中的实现

####  3.1.3. express

```javascript

router.get('*', function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");
  res.header("Access-Control-Allow-Methods", "PUT,POST,GET,DELETE,OPTIONS");
  res.header("X-Powered-By", ' 3.2.1')
  res.header("Content-Type", "application/json;charset=utf-8");
  next();
});

```

###  3.2. 权限

后台服务需要保护好隐私不被泄露,避免路径攻击和端口暴露等问题

##  4. 必须实现的部分


### 用户 /user

```
    GET:

    http://ip:port/user?action={}&username={}&password={}&{}{}{}

    action:
        query(default)
        query_strategy |  status = all / running

    username:
        admin(default)
    password
        admin(default)

    POST:

    http://ip:port/user?action={}&username={}&password={}&{}{}{}

    action:
        change_password: 更改账户密码| password={}
        change_phone: 更改手机号| phone={}
        change_coins: 更改积分| coins={}
        subscribe_strategy: 订阅策略| strategy_id={} | last={} | cost_coins={}
        unsubscribe_strategy: 取消订阅策略| strategy_id={}
        subscribe_code: 订阅品种| code={}

        new_portfolio


    DELETE

    http://ip:port/user?action={}&username={}&password={}&{}{}{}


    #TODO
    action:
        del_portfolio
        del_account

```

```json
{
    "result": {
        "user_cookie": "USER_gcThpftb",
        "username": "admin",
        "password": "admin",
        "phone": "18626855195",
        "level": "l1",
        "utype": "guests",
        "coins": 8680,
        "coins_history": [
            [
                120,
                "xxx1",
                "2019-01-18",
                2,
                "f0c97478-1b15-11e9-9c3c-9cb6d020b9c2",
                "subscribe"
            ],
            [
                0,
                "xxx1",
                "2019-01-18",
                0,
                "055c9900-1b16-11e9-a217-9cb6d020b9c2",
                "unsubscribe"
            ],
            [
                1200,
                "xxx2",
                "2019-01-18",
                24,
                "1950d708-1b16-11e9-a62e-9cb6d020b9c2",
                "subscribe"
            ]
        ],
        "money": 200000,
        "subuscribed_strategy": {
            "xxx1": {
                "lasttime": 2,
                "start": "2019-01-18",
                "strategy_id": "xxx1",
                "end": "2019-01-22",
                "status": "canceled",
                "uuid": "f0c97478-1b15-11e9-9c3c-9cb6d020b9c2"
            },
            "xxx2": {
                "lasttime": 24,
                "start": "2019-01-18",
                "strategy_id": "xxx2",
                "end": "2019-02-28",
                "status": "running",
                "uuid": "1950d708-1b16-11e9-a62e-9cb6d020b9c2"
            }
        },
        "subscribed_code": [
            "RB"
        ]
    }
}
```

### 组合 /portfolio

```
    GET:
    http://ip:port/portfolio?action={}&username={}&password={}&{}{}{}

    params:
        action:

            - get_accounts(默认)
            - get_cash

        portfolio_cookie (必须项)
        user_cookie (必须项)

    POST:

    http://ip:port/user?action={}&username={}&password={}&{}{}{}

    action:
        delete_account: 删除账户 | account_cookie


```




### 账户 /account





### 交易 /trade



###  4.3. 行情查询部分 /marketdata & /data

功能性的API,分别代表着 日线/分钟线/实时(5档)/分笔数据

####  4.3.1. URI总规则 GENERAL URI RULE
```
总URI为 http://[ip]:[port]/[market_type]/[frequence]?code=[]&start=[]&end=[]
```

####  4.3.2. 股票日线 STOCK DAY
```
http://[ip]:[port]/marketdata/stock/day?code=[]&start=[]&end=[]
```

当不给定结束日期的时候,返回的就是直到当前的数据

####  4.3.3. 股票分钟线 STOCK MINDATA
```
http://[ip]:[port]/marketdata/stock/min?code=[]&start=[]&end=[]
```

当不给定结束日期的时候,返回的就是直到当前的数据

####  4.3.4. 股票实时上下五档 STOCK REALTIME PRICE 5-ASK/BID
```
http://[ip]:[port]/marketdata/stock/price?code=xxxxxx
```

实时返回股票的L1上下五档的行情数据

####  4.3.5. 股票分笔数据 STOCK TRANSACTION
```
http://[ip]:[port]/marketdata/stock/transaction?code=[]&start=[]&end=[]
```
code 指的是具体的股票代码
start 指的是分笔开始的时间
end 指的是分笔结束的时间

####  4.3.6. 股票财务数据
```
http://[ip]:[port]/marketdata/stock/info?code=[]&time=[]
```
code 指的是具体的股票
time 指的是时间段

如 code=000001 time=2018Q1 指的是000001的2018年1季度

time的格式为: YEAR['YYYY']+Q+times[1,2,3,4](1- 1季度财报 2- 半年度财报 3- 3季度财报 4- 年报)

####  4.3.7. 期货日线
```
http://[ip]:[port]/marketdata/future/day?code=[]&start=[]&end=[]
```

####  4.3.8. 期货分钟线
```
http://[ip]:[port]/marketdata/future/min?code=[]&start=[]&end=[]
```
###  4.4. 实时行情推送 /realtime
```
/realtime 推送指的是 建立一个websocket链接:
```
1. user login [Handler]

2. auth []

3. send_req [front end/client]

4. make connection

5. data transport




#### 4.5.1 全部账户列表查询


```
http://[ip]:[port]/accounts/all
```

#### 4.5.2 单个账户查询


```
http://[ip]:[port]/accounts?account_cookie=xxx

```

### 4.6 风险查询 /risks
```
http://[ip]:[port]/risks?account_cookie=xxx
```


### 4.7 下单 /trade | /tradeinfo


#### 4.7.1 静态信息查询

```
http://[ip]:[port]/tradeinfo



    ?func=ping  ping 服务器
    ?func=clients 查询当前的可用客户端
    ?func=accounts 查询当前的账户
    ?func=positions&account=xxx 查询账户持仓
    ?func=orders&status 查询订单

    下单/撤单功能不在此handler提供
    
```


#### 4.7.2 websocket接口

```
http://[ip]:[port]/trade
```

message:

1. create_account 创建一个账户
2. query_portfolio 查询组合
3. query_history 查询账户交易历史
4. trade_{code}_{tradeprice}_{tradeamount}_{tradetowards}_{tradetime} 交易
5. cancel_{orderid}
6. sendorder_