import requests
import time
import random
import csv
import hashlib

C = 'leftMenuLastMode=COLLAPSE; xlly_s=1; plugin_home_downLoad_cookie=%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6; leftMenuModeTip=shown; cookie2=11c3881e00dd625d92907148a372daf0; t=9e974bfbb28c81e3a1df7225baddbccc; _tb_token_=f677eeee7ebee; __cn_logon__=false; keywordsHistory=%E7%BE%BD%E7%BB%92%E6%9C%8D; _samesite_flag_=true; tracknick=; taklid=d880687cbdf746f2a51e613a842ce84e; cna=omEUIi0YJ3MCAbfj85vt05cR; _csrf_token=1770882228795; mtop_partitioned_detect=1; _m_h5_tk=fad153b067181bfcf57c58433e7b9a21_1770911199524; _m_h5_tk_enc=ed1f1ac333c0d0e41d9feecfaf20eed2; union={"amug_biz":"comad","amug_fl_src":"sem_bing","creative_url":"https%3A%2F%2Fwww.1688.com%2Fzw%2Fpage.html%3FhpageId%3Dold-sem-pc-list%26keywords%3D%25E7%25BE%25BD%25E7%25BB%2592%25E6%259C%258D%26cosite%3Dbingjj%26location%3Dlanding_t4%26trackid%3D8852366114669144018230490%26spm%3Da2638t.b_30496503.szyx_head.submit%26keywordid%3D%26bt%3D%26exp%3Dsidebar%253AC%253BbuyerIntent%253AB%253BpcDacuIconExp%253AB%253BpcCpxGuessExp%253AB%253BpcCpxCpsExp%253AB%253BhotBangdanExp%253AB%26ptid%3D0177000000085393427f0799538482d7","creative_time":1770904308741}; _user_vitals_session_data_={"user_line_track":true,"ul_session_id":"ew284y8gc3a","last_page_id":"www.1688.com%2Fo9r7uep78cf"}; tfstk=g4xtHDq8RXcM3viIwl0nnwbBAsMHH2vNvCJ7msfglBdpFLPGlN6bdJ1pg1bGfrVX9KRvsFvXmttvTG_2SsfGMip2wvcoq0vwQi7jZbmoixQD8i5jmighAO4oi7coq0vs5OSDdbYMpbfGhTqfcN11d61FFlZ6GNaQd6WVh56bfvpCT6Z_5sZbAp6Rhs6XGiMdA6WccOOf5vpCTtsfGb_aBs21MoLd8_YRPkaLDoKdBNCYm6Zv6HZlW_NFOoZfoO7ted1Lcotpl4TzS1gzKsSG_pB9g0rNfZLXjMtsOmsWzBKAPg3mQN9vJISMAxa1NFAGAhT8ho9dXsOlQNFt9_twd3SC-0MJdHRMQHp0hm6HZ69wfinSUGI11MBemXr1MeTXjNS41jC2vpt6kglMq33nE7fRnPMKprzV59yqJ-dP2AYRJ9CoKy44uwXFp_DKprzV59WdZvm3ur7hL; isg=BF9fYv7ASptmW06Hkn56ELYn7rPpxLNmA6P7zPGsgY53gH8C-JVvt8RZQlBbI4ve'
user = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0'
headers = {
    'cookie': C,
    'user-agent': user,
}
# 加密参数: 通过调试得到
# salt = time.time()
# string = f'pcsem羽绒服{salt}csb44T%34CiKj&FyRbCBJ'
# # MD5 = hashlib.md5()
# # MD5.update(string.encode('utf-8'))
# # sign = MD5.hexdigest()
# sign = hashlib.md5(string.encode('utf-8')).hexdigest()

file_csv = open(file='product_Year.csv', mode='w', encoding='utf-8-sig')
fields = ["company","bangdan_name","ranking","subject",'price', "unit","chengjiaov", "saleVolume","odUrl"]
# ['公司','榜单名', '排名', '商品名称单价','单位','成交金额','销售量','商品网址']
file_data = csv.DictWriter(file_csv, fieldnames=fields, delimiter=';')
file_data.writeheader()

for pagenum in range(5):

    for page_index in range(7):

        salt = int(time.time() * 1000)  # 时间戳
        string = f'pcsem春节礼品{salt}csb44T%34CiKj&FyRbCBJ'
        sign = hashlib.md5(string.encode('utf-8')).hexdigest()

        url = 'https://p4psearch.1688.com/hamlet/async/v1.json?' # 'https://p4psearch.1688.com/hamlet/async/v1.json?'
        # 请求载荷
        data = {
            'beginpage': pagenum,
            'asyncreq': page_index,
            'keywords':'',
            'keyword': '春节礼品',# '烧烤' ,# '羽绒服', #
            'sortType':'',
            'descendOrder':'',
            'province':'',
            'city':'',
            'priceStart':'',
            'priceEnd':'',
            'dis':'',
            'ptid': '0177000000085393427f0799538482d7',# '0177000000085393427f0799538482d7', # '0177000000085203b0ab0d5c147fdb7b', #
            'exp':'pcSemFumian:C;pcDacuIconExp:B;pcCpxGuessExp:B;qztf:F;wysiwyg:B;buyerIntent:B;asst:D;sidebar:C;pcCpxCpsExp:B;hotBangdanExp:B;pcSemWwClick:A;pcSemDownloadPlugin:A',
            'cosite':'bingjj',
            'salt': salt,
            'sign':sign,
            'hmaTid':'3',
            'hmaQuery':'graphDataQuery',
            'pidClass':'pc_list_336',
            'cpx':'cpc,cpt,free,nature',
            'api':'pcSearch',
            'pv_id':'',
        }
        # 获取的json格式的响应
        response = requests.get(url, params=data, headers=headers)
        print("状态码:", response.status_code)
        print("响应头:", response.headers.get('Content-Type'))
        print("响应前10字符:", response.text[:10])
        response_json = response.json()
        info_list = response_json['module']['offer']['list']

        for item in info_list:
            offerBangdan = item.get('offerBangdan')
            zhurong = item.get('zhurong')

            # 先给所有变量设默认值
            bangdan_name = '未上榜'
            ranking = 0
            chengjiaov = 0  # 或 None，根据业务需求

            if isinstance(offerBangdan, dict):
                bangdan_name = offerBangdan.get('bangdanName', '未上榜')
                ranking = offerBangdan.get('ranking', 0)

            if isinstance(zhurong, dict):
                try:
                    # 安全取值，避免多层get报错
                    chengjiaov = zhurong.get('10003', {}).get('salesDpa', [{}])[0].get('v', 0)
                except (IndexError, AttributeError):
                    chengjiaov = 0


            data_dict = {
                "company": item.get('company'), # 公司
                "bangdan_name": bangdan_name, # 榜单名
                "ranking": ranking,  # 排名
                "subject": item.get('subject'),  # 商品名称
                'price': item.get('price'), # 单价
                "unit": item.get('unit'), # 单位
                "chengjiaov": chengjiaov,  # 成交金额
                "saleVolume": item.get('saleVolume').replace('+', '') ,   # 销售量
                "odUrl": item.get('odUrl') # 商品网址
            }
            print(data_dict)
            file_data.writerow(data_dict)
            # 防止反爬触发
            # time.sleep(random.randint(1, 2))
    time.sleep(random.randint(1, 3))


    