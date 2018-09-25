import requests
# 此方法已不适用于知乎
# 知乎已经不用post传到www.zhihu.com/login/phone_num获取cookie了
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re

session = requests.session()
# 通过cookielib里面的LWPCookieJar可以生成一个save方法
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")


# 尝试加载cookie
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")




# 设置user_Agent(每一个浏览器去访问都会带上自己的浏览器信息)
user_Agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"
# header的固定写法
header = {
    "HOST":"www.zhihu.com",
    "Referer":"www.zhihu.com",
    'user_Agent':user_Agent

}


def is_login():
    # 通过个人中心返回状态码判断是否已经登录
    inbox_url = "https://www.zhihu.com/inbox"
    # allow_redirects来设置是否重定向 否则会跳转到重定向的页面从而获取到200
    response = session.get(inbox_url,headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True

def get_xsrf():
    # 当次访问服务器会给一个临时的xsrf值在文本中，需要将这个值与账号密码一同传往服务器来模拟登陆
    # response = requests.get("https://www.zhihu.com",headers = header)
    # 用session效率更高，代表每一次链接，不用每次都去requests去建立一次链接
    response = session.get("https://www.zhihu.com", headers=header)
    # 因为知乎现在不用xsrf了，这个xsrf是随便写的
    # text = '<input type="hidden" name="_xsrf" value="123vsfvsf8948948v"/>'
    # 注意问号做非贪婪匹配,re.DOTALL表示匹配所有行，默认re只匹配一行，需要加上DOTALL
    match_obj = re.match('.*name="_xsrf" value="(.*?)"',response.text,re.DOTALL)
    if match_obj:
        return(match_obj)
    else:
        return ""

def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html","wb") as f:
        f.write(response.text.encode(encoding="utf-8"))
    print("ok")


def zhihu_login(account,password):
    #知乎登录
    if re.match("1\d{10}",account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password
        }
        # 同理把requests换成了session
        response_text = session.post(post_url,data=post_data,headers=header)
        # 这里的save需要LWPCookieJar来实例cookies
        session.cookies.save()