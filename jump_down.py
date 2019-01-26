"""
author: thomaszdxsn
"""
from http.cookies import SimpleCookie
from datetime import datetime
import json
import asyncio
import aiohttp


from src.sdk.jump_liquid import JumpLiquidWebsocket


def cookies2dict(raw):
    cookie_jar = SimpleCookie()
    cookie_jar.load(raw)
    result = {}
    for key, morsel in cookie_jar.items():
        result[key] = morsel.value
    return result

ws_url = 'wss://www.liquidcryptotrading.com/traderWorkstationWS'

data1 = {
    'msgType': 2,
    'reqMsgType': 4,
    'timestamp': round(datetime.now().timestamp(), 3)
}
data2 = {
    'msgType': 11,
    'blur': True
}
data3 = json.loads(r'{"msgType":12,"info":"settings","clientInfo":{"version":"0.1.11","browserData":{"ua":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36","browser":{"name":"Chrome","version":"71.0.3578.98","major":"71"},"engine":{"version":"537.36","name":"WebKit"},"os":{"name":"Mac OS","version":"10.14.1"},"device":{},"cpu":{}},"finger":3628360444,"userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36","browser":"Chrome","browserVersion":"71.0.3578.98","isIE":false,"isChrome":true,"isFirefox":false,"isSafari":false,"isMobileSafari":false,"isOpera":false,"engine":"WebKit","engineVersion":"537.36","os":"Mac OS","osVersion":"10.14.1","isWindows":false,"isMac":true,"isLinux":false,"isUbuntu":false,"isSolaris":false,"mobile":false,"mobileAndroid":false,"mobileOpera":false,"mobileWindows":false,"mobileBlackBerry":false,"mobileIOS":false,"isIphone":false,"isIpad":false,"isIpod":false,"screenPrint":"Current Resolution: 2560x1440, Available Resolution: 2560x1417, Color Depth: 24, Device XDPI: undefined, Device YDPI: undefined","colorDepth":24,"resolution":"2560x1440","availableResolution":"2560x1417","plugins":"Chrome PDF Plugin, Chrome PDF Viewer, Native Client","isLocalStorage":true,"isSessionStorage":true,"isCookie":true,"tz":"中国标准时间","language":"zh-CN"},"cookies":"can_dayOrder=\"2|1:0|10:1546507826|12:can_dayOrder|8:RmFsc2U=|7392dffc10870216d762ea198ce8a691213381e8947476d8d585a4c9d392263b\"; can_GTCOrder=\"2|1:0|10:1546507826|12:can_GTCOrder|8:RmFsc2U=|87abc70eaff4e2bf813796b5f29353f5d9f3903fc1d8b886b85fbce3149d9060\"; can_trade=\"2|1:0|10:1546507826|9:can_trade|8:RmFsc2U=|b12020b0f74d624cb942565dce204cde79b387b9061b99d6a1f6bc2ef777bf6c\"; can_admin=\"2|1:0|10:1546507826|9:can_admin|8:RmFsc2U=|048391aabc2aa18c30f32d504999fdb90ace56f0d8af941401d66797c97d599c\"; can_rfs=\"2|1:0|10:1546507826|7:can_rfs|8:RmFsc2U=|9d54ff91b4c1efdc34f4513639ad85440946d5552d82cf67d8afd125531c22c1\"; user_settings_profile=OHFI2; user=\"2|1:0|10:1546507826|4:user|8:T0hGSTI=|7be2716dfbaf8f8e91a392848a66c0f7832043f8dc3f41e3c7842d61e5467ec9\"","localStorage":{"OHFI2_ChangeLogHash":"-1371930295","OHFI2_UserDataV1":"{\"panelHeights\":{\"h1\":70,\"h2\":30},\"symbols\":[\"BCHUSD\",\"BSVUSD\",\"BTCUSD\",\"ETCUSD\",\"ETHUSD\",\"LTCUSD\",\"XLMBTC\",\"XLMUSD\",\"XRPUSD\"]}"},"sessionStorage":{}}')

headers = {
    'Host': 'www.liquidcryptotrading.com',
    'Origin': 'https://www.liquidcryptotrading.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}
cookies = cookies2dict('__cfduid=d0f94f18b0b5247257fb7a328ada5e5901545897180; can_dayOrder="2|1:0|10:1546507826|12:can_dayOrder|8:RmFsc2U=|7392dffc10870216d762ea198ce8a691213381e8947476d8d585a4c9d392263b"; can_GTCOrder="2|1:0|10:1546507826|12:can_GTCOrder|8:RmFsc2U=|87abc70eaff4e2bf813796b5f29353f5d9f3903fc1d8b886b85fbce3149d9060"; can_trade="2|1:0|10:1546507826|9:can_trade|8:RmFsc2U=|b12020b0f74d624cb942565dce204cde79b387b9061b99d6a1f6bc2ef777bf6c"; can_admin="2|1:0|10:1546507826|9:can_admin|8:RmFsc2U=|048391aabc2aa18c30f32d504999fdb90ace56f0d8af941401d66797c97d599c"; can_rfs="2|1:0|10:1546507826|7:can_rfs|8:RmFsc2U=|9d54ff91b4c1efdc34f4513639ad85440946d5552d82cf67d8afd125531c22c1"; user_settings_profile=OHFI2; user="2|1:0|10:1546507826|4:user|8:T0hGSTI=|7be2716dfbaf8f8e91a392848a66c0f7832043f8dc3f41e3c7842d61e5467ec9"')


async def main():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(), headers=headers, cookies=cookies) as session:
        async with session.ws_connect(ws_url) as wss:
            print(wss.send_json)
            for payload in (data1, data2, data3):
                await wss.send_json(payload)
            async for msg in wss:
                print(msg)


asyncio.get_event_loop().run_until_complete(main())

