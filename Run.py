import requests
import json
import time
import hashlib
import random
import sys


class ShowProcess():
    """
    显示处理进度的类
    调用该类相关函数即可实现处理进度的显示
    """
    i = 0 # 当前的处理进度
    max_steps = 0 # 总共需要处理的次数
    max_arrow = 38 #进度条的长度
    infoDone = 'done'

    # 初始化函数，需要知道总共的处理次数
    def __init__(self, max_steps, infoDone = 'Done'):
        self.max_steps = max_steps
        self.i = 0
        self.infoDone = infoDone

    # 显示函数，根据当前的处理进度i显示进度
    def show_process(self, i=None):
        if i is not None:
            self.i = i
        else:
            self.i += 1
        num_arrow = int(self.i * self.max_arrow / self.max_steps) #计算显示多少个'>'
        num_line = self.max_arrow - num_arrow #计算显示多少个'-'
        percent = self.i * 100.0 / self.max_steps #计算完成进度，格式为xx.xx%
        process_bar = '[' + '#' * num_arrow + '-' * num_line + ']'\
                      +  "%.2f%%" %percent+ '\r' #带输出的字符串，'\r'表示不换行回到最左边
        sys.stdout.write(process_bar) #这两句打印字符到终端
        sys.stdout.flush()
        if self.i >= self.max_steps:
            self.close()

    def close(self):
        print('')
        print(self.infoDone)
        self.i = 0

# Generate table Randomly
alphabet = list('abcdefghijklmnopqrstuvwxyz')
random.shuffle(alphabet)
table = ''.join(alphabet)[:10]


def MD5(s):
    return hashlib.md5(s.encode()).hexdigest()


def encrypt(s):
    result = ''
    for i in s:
        result += table[ord(i) - ord('0')]
    # print(result)
    return result


def Run(IMEI=None):
    if IMEI is None:
        # Input to IMEI
        if(len(sys.argv) > 1):
            IMEI = sys.argv[1]
        else:
            IMEI = str(input("Please Input Your IMEI Code:"))
        if(len(IMEI) != 32):
            exit("IMEI Format Error!")

        if (len(sys.argv) > 2 and sys.argv[2].upper() == 'Y'):
            pass
        else:
            print("Your IMEI Code:", IMEI)
            Sure = str(input("Sure?(Y/N)"))
            if(Sure == 'Y' or Sure == 'y'):
                pass
            else:
                exit("User Aborted.")

    API_ROOT = 'http://client3.aipao.me/api'  # client3 for Android
    Version = '2.19'

    # Login
    TokenRes = requests.get(
        API_ROOT + '/%7Btoken%7D/QM_Users/Login_AndroidSchool?IMEICode=' + IMEI)
    TokenJson = json.loads(TokenRes.content.decode('utf8', 'ignore'))

    # headers
    token = TokenJson['Data']['Token']
    userId = str(TokenJson['Data']['UserId'])
    timespan = str(time.time()).replace('.', '')[:13]
    auth = 'B' + MD5(MD5(IMEI)) + ':;' + token
    nonce = str(random.randint(100000, 10000000))
    sign = MD5(token + nonce + timespan + userId).upper()  # sign为大写

    header = {'nonce': nonce, 'timespan': timespan,
              'sign': sign, 'version': Version, 'Accept': None, 'User-Agent': None, 'Accept-Encoding': None, 'Connection': 'Keep-Alive'}

    # Get User Info

    GSurl = API_ROOT + '/' + token + '/QM_Users/GS'
    GSres = requests.get(GSurl, headers=header, data={})
    GSjson = json.loads(GSres.content.decode('utf8', 'ignore'))

    Lengths = GSjson['Data']['SchoolRun']['Lengths']
    School = GSjson['Data']['SchoolRun']['SchoolName']
    Name = GSjson['Data']['User']['NickName']
    Num = GSjson['Data']['User']['UserName']
    Sex = GSjson['Data']['User']['Sex']
    print('身份验证成功')
    #print('-----------------快跑测试版------------------')
    print('--------'+School+'--------'+Num+'--------')
    print('-------- '+Name+' --------------'+Sex+'-------------')
    #print('------------是'+Sex+'的,就要跑'+str(Lengths)+'米--------------')
    print('-------- '+str(Lengths)+'米--------------开跑'+'------------')
    # Start Running
    SRSurl = API_ROOT + '/' + token + \
        '/QM_Runs/SRS?S1=30.534736&S2=114.367788&S3=' + str(Lengths)
    SRSres = requests.get(SRSurl, headers=header, data={})
    SRSjson = json.loads(SRSres.content.decode('utf8', 'ignore'))

    # Generate Runnig Data Randomly
    RunTime = str(random.randint(720, 1000))  # seconds
    RunDist = str(Lengths + random.randint(0, 3))  # meters
    RunStep = str(random.randint(1300, 1600))  # steps

    # Running Sleep
    StartT = time.time()
    process_bar = ShowProcess(int(RunTime), 'DONE!')
    for i in range(int(RunTime)):
        process_bar.show_process()
        time.sleep(1)
        #print("Current Minutes: %d Running Progress: %.2f%%\r" %
              #(i / 60, i * 100.0 / int(RunTime)), end='')
    print("")
    print("Running Seconds:", time.time() - StartT)

    # print(SRSurl)
    # print(SRSjson)

    RunId = SRSjson['Data']['RunId']

    # End Running
    EndUrl = API_ROOT + '/' + token + '/QM_Runs/ES?S1=' + RunId + '&S4=' + \
        encrypt(RunTime) + '&S5=' + encrypt(RunDist) + \
        '&S6=&S7=1&S8=' + table + '&S9=' + encrypt(RunStep)

    EndRes = requests.get(EndUrl, headers=header)
    EndJson = json.loads(EndRes.content.decode('utf8', 'ignore'))

    print("-----------------------")
    print("Time:", RunTime)
    print("Distance:", RunDist)
    print("Steps:", RunStep)
    print("-----------------------")

    if(EndJson['Success']):
        print("[+]OK:", EndJson['Data'])
    else:
        print("[!]Fail:", EndJson['Data'])


def main():
    Run()


if __name__ == '__main__':
    main()
