# -*- coding: utf-8 -*-

import os.path
import requests
import time
import json
import re

################### Config #############################
# Windows推荐直接双击脚本运行，或使用CMD/PowerShell运行
# 不推荐使用Python IDLE运行（执行输出会乱码）
# 如果使用CMD/PowerShell运行过程中，"卡"住，请多敲几下回车即可

cookie_xsid = ''


########################################################


def getTs():
    return int(time.time() * 1000)


class AutoCompletPapers():
    def __init__(self, session, courseId, title):

        """
        自动完成小节习题（仅支持已过提交日期的习题）
        :return:
        """
        self.mid = None
        self.Session = session
        self.courseId = courseId
        self.cookieXsidUser = None
        self.title = title
        self.answerTable = {
            "-1": '未作答',
            "0": 'A',
            "1": 'B',
            "2": 'C',
            "3": 'D',
            "4": 'E',
            "5": 'F',
            "6": 'G',
        }
        self.judge = {
            "-1": '未作答',
            "1": 'A',
            "2": 'B',
        }
        self.sectionList = \
            self.get('https://www.cqooc.com/json/chapter/lessons?courseId=' + self.courseId).json()['data'][0]['body']

        try:
            self.name = self.get(f'https://www.cqooc.com/account/session/api/profile/get?ts={getTs()}').json().get(
                'name')
        except:
            self.name = input("名字获取失败！请输入你的名字（真实名字）: ")

    def get(self, url, headers=None):
        # 防止请求异常抛出，异常自动重新请求
        while True:
            try:
                return self.Session.get(url, headers=headers)
            except:
                print("请求异常，重试中...")
                continue

    def post(self, url, json=None, headers=None, data=None):
        while True:
            try:
                return self.Session.post(url, json=json, headers=headers, data=data)
            except:
                print("请求异常，重试中...")
                continue

    def getIds(self, paperId):
        # Referer
        response = self.get(f'https://www.cqooc.com/test/api/paper/info?id={paperId}&ts={getTs()}')
        data = response.json()

        return {"cid": data.get('parentId'),
                "sid": self.sectionList.get(data.get('parentId'))[0]
                }

    def saveAnswersFromDue(self, papersIds):
        file = open(f'{self.title}.txt', 'w+')
        print(f"开始导出，共 {len(papersIds)} 次测试")
        for id_index, id in enumerate(papersIds):

            req_url = 'https://www.cqooc.com/test/api/paper/get?id=' + str(id) + '&ts=1581869807566'

            response = self.get(req_url, headers={
                'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={id}&id={self.courseId}&sid=381090&cid=158386&mid=12166414',
            })
            submitEnd = response.json()['submitEnd']
            if submitEnd > time.time() * 1000:
                print(f"未过期，跳过! {papersIds.get(id)}")
                continue
            if '503 Service Temporarily' in response.text:
                print(str(id) + " 失败！！")
                continue

            body = response.json()['body']
            if body is None: continue

            for i in body:
                if i['questions'] != []:
                    if i['desc'] == '判断题':
                        questions_type = "[判断题] "
                    elif i['desc'] == '多选题':
                        questions_type = "[多选题] "
                    elif i['desc'] == '单选题':
                        questions_type = "[单选题] "
                    else:
                        questions_type = ''

                    for question in i['questions']:
                        # 提取问题
                        if '<p>' in question['question']:
                            question_re = re.findall('>(.*?)<', question['question'], re.S)
                            question_plus = ''
                            for t in question_re:
                                question_plus += t.replace('&nbsp;', '')
                            file.write(questions_type + question_plus.lstrip() + '\n')
                        else:
                            question_plus = question['question'].replace('\n', '').replace('\r', '')
                            file.write(questions_type + question_plus.lstrip() + '\n')

                        # 处理判断题
                        if i['desc'] == '判断题':
                            file.write('答案: ')
                            file.write(self.judge[question['body']['answer'][0]])
                        # 非判断题
                        else:
                            # 遍历选项并写入
                            for index, j in enumerate(question['body']['choices']):
                                file.write('  ' + self.answerTable[str(index)] + '、' + j + '\n')
                            file.write('答案: ')
                            # 写入答案，多选题需遍历
                            for x in question['body']['answer']:
                                file.write(self.answerTable[x] + ' ')
                        file.write('\n\n')
            # 请求过快会503
            print(f"[{id_index + 1}/{len(papersIds)}] {papersIds.get(id)}")
            time.sleep(1)
        print("写入完成！", os.path.abspath(f'{self.title}.txt'))

    def saveAnswersFromUser(self, papersIds):
        # 保存已作答题目的答案

        file = open(f'{self.title}.txt', 'w+')
        print(f"开始导出，共 {len(papersIds)} 次测试")
        for id_index, id in enumerate(papersIds):
            data = self.get(f'https://www.cqooc.com/json/test/result/search?testID={id}', headers={
                'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={id}&id={self.courseId}'
                           f'&sid=360456&cid=149658&mid=12158213',
            })

            time.sleep(0.5)

            req_url = f'https://www.cqooc.com/test/api/paper/get?id={id}'

            response = self.get(req_url, headers={
                'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={id}&id={self.courseId}'
                           f'&sid=360456&cid=149658&mid=12158213',
            })

            body = response.json()['body']
            if body is None: continue

            for i in body:
                if i['questions']:
                    if i['desc'] == '判断题':
                        questions_type = "[判断题] "
                    elif i['desc'] == '多选题':
                        questions_type = "[多选题] "
                    elif i['desc'] == '单选题':
                        questions_type = "[单选题] "
                    else:
                        questions_type = ''

                    for question in i['questions']:
                        # 提取问题
                        if '<p>' in question['question']:
                            question_re = re.findall('>(.*?)<', question['question'], re.S)
                            question_plus = ''
                            for t in question_re:
                                question_plus += t.replace('&nbsp;', '')
                            file.write(questions_type + question_plus.lstrip() + '\n')
                        else:
                            question_plus = question['question'].replace('\n', '').replace('\r', '')
                            file.write(questions_type + question_plus.lstrip() + '\n')

                        if not data.json()['data']:
                            answers = '-1'
                        else:
                            answers = data.json()['data'][0]['body'][0]['q' + question['id']]
                        if i['desc'] == '判断题':
                            answer = self.judge[answers]
                            # 写入答案
                            file.write('答案: ')
                            file.write(answer)
                        # 非判断题
                        else:
                            # 遍历选项并写入
                            if data.json()['data'] == []:
                                answer = ['-1']
                            else:
                                answer = answers
                            tempAnswer = ""
                            for tag in answer:
                                tempAnswer += self.answerTable[str(tag)]
                            for index, j in enumerate(question['body']['choices']):
                                file.write('  ' + self.answerTable[str(index)] + '、' + j.lstrip() + '\n')
                            file.write('答案: ')
                            # 写入答案，多选题需遍历
                            file.write(tempAnswer + ' ')
                        file.write('\n\n')
            print(f"[{id_index + 1}/{len(papersIds)}] {papersIds.get(id)}")
            time.sleep(1)
            file.write('\n\n')
        print("写入完成！", os.path.abspath(f'{self.title}.txt'))

    def getAnswers(self, paperId):
        # 获取答案
        req_url = f'https://www.cqooc.com/test/api/paper/get?id={paperId}&ts={getTs()}'

        try:
            ids = self.getIds(paperId)
        except TypeError:
            return None

        response = self.get(req_url, headers={
            'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={paperId}&id={self.courseId}'
                       f'&sid={ids.get("sid")}&cid={ids.get("cid")}&mid={self.mid}',
        })

        submitEnd = response.json()['submitEnd']
        if submitEnd > time.time() * 1000:
            return -1
        body = response.json()['body']
        answers = {}
        try:
            for i in body:
                if i['questions'] != []:
                    for question in i['questions']:
                        answer = question['body']['answer']
                        if len(answer) == 1:
                            answer = answer[0]
                        answers["q" + question['id']] = answer
            return answers
        except:
            return None

    def getAnswersFromUser(self, paperId):
        # 获取答案（从另一个用户）
        self.cookieXsidUser = input(
            "请输入已作答用户的cookie(xsid): ") if self.cookieXsidUser is None else self.cookieXsidUser

        # ids = self.getIds(paperId)

        session = requests.session()
        session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) ' \
                            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
        session.headers['Connection'] = 'close'
        session.headers['cookie'] = 'xsid={}; player=1'.format(self.cookieXsidUser)

        data = session.get('https://www.cqooc.com/json/test/result/search?testID=' + str(paperId), headers={
            'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={paperId}&id={self.courseId}&sid=360456&cid=149658&mid={self.mid}',
        })

        time.sleep(0.5)

        req_url = 'https://www.cqooc.com/test/api/paper/get?id=' + str(paperId)
        response = session.get(req_url, headers={
            'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?do?tid={paperId}&id={self.courseId}&sid=360456&cid=149658&mid=12158213',
        })

        if response.json().get('code') == 401:
            input("xsid有误，请检查！")
            return -2
        body = response.json()['body']
        answers = {}
        try:
            for i in body:
                if i['questions'] != []:
                    for question in i['questions']:
                        answer = data.json()['data'][0]['body'][0]['q' + question['id']]
                        if len(answer) == 1:
                            answer = answer[0]
                        answers["q" + question['id']] = answer
            return answers
        except:
            return None

    def sendAnswers(self, mode=None):
        """
        :param mode: due 已过期题目获取答案提交  非due  从另一个用户获取答案提交
        :return:
        """
        info = self.get('https://www.cqooc.com/user/session?xsid=' + cookie_xsid).json()
        self.mid = \
            self.get(f'https://www.cqooc.com/json/mcs?ownerId={info["id"]}&courseId={self.courseId}&ts={getTs()}',
                     headers={
                         "Referer": f'https://www.cqooc.com/learn/mooc/structure?id={self.courseId}'
                     }).json()['data'][0]['id']

        papersList = self.get(
            f'https://www.cqooc.com/json/exam/papers?limit=200&start=1&courseId={self.courseId}&select=id,title&ts={getTs()}')

        papersInfo = {}
        for i in papersList.json()['data']:
            papersInfo[str(i.get('id'))] = i.get('title')

        print("\n[{}] 共 {} 题".format('过期题目作答' if mode == 'due' else '拷贝答案作答', len(papersInfo)))
        for index, id in enumerate(papersInfo):

            answers = self.getAnswers(id) if mode == 'due' else self.getAnswersFromUser(id)

            if answers == -1:
                print("{}/{} [{}] 未过提交日期，跳过！".format(len(papersInfo), index + 1, papersInfo[id]))
                time.sleep(1)
                continue
            elif answers is None:
                print(
                    f"[{index + 1}/{len(papersInfo)}] {'无测试题目，跳过！' if mode == 'due' else '未获取到答案，跳过！'} {papersInfo[id]} ")
                time.sleep(1)
                continue
            elif answers == -2:
                return

            # 检查是否已经作答
            isAnswer = self.get(f'https://www.cqooc.com/json/test/result/search?testID={id}&ts={getTs()}', headers={
                'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={id}&id={self.courseId}&sid=488839&cid=197038&mid={self.mid}'
            }).json()

            if isAnswer['data']:
                print(f"[{index + 1}/{len(papersInfo)}] 已作答，跳过！ {papersInfo[id]}")
                # print("{}/{} [{}] 已作答，跳过！".format(len(papersInfo), index + 1, papersInfo[id]))
                time.sleep(1)
                continue

            response = self.post('https://www.cqooc.com/test/api/result/add', headers={
                'Referer': f'https://www.cqooc.com/learn/mooc/testing/do?tid={id}&id={self.courseId}&sid=307978&cid=131676&mid={self.mid}',
            }, data=json.dumps({
                "ownerId": info.get('id'),
                "username": info.get('username'),
                "name": self.name,
                "paperId": str(id),
                "courseId": self.courseId,
                "answers": answers,
                "classId": ""
            }))

            if response.json().get('code') == 100:
                print(f"[{index + 1}/{len(papersInfo)}] 已超过提交最大次数！ {papersInfo[id]}")
                # print("{}/{} [{}] 已超过提交最大次数！".format(len(papersInfo), index + 1, papersInfo[id]))
            else:
                print(f"[{index + 1}/{len(papersInfo)}] 得分: {response.json().get('score')} {papersInfo.get('id')}")
                # print("{}/{} [{}] 得分: {}".format(len(papersInfo), index + 1, papersInfo[id], response.json().get('score')))

            time.sleep(1)


class AutoCompleteOnlineCourse:
    def __init__(self) -> None:
        if cookie_xsid == '':
            input("请添加xsid")
            exit(0)
        # HEADERS
        session = requests.Session()
        session.headers['Cookie'] = 'player=1; xsid=' + cookie_xsid
        # session.headers['Connection'] = 'close'
        session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        session.headers['Host'] = 'www.cqooc.com'
        session.keep_alive = False
        self.Session = session
        self.CompleteCourse = None
        self.courseId = None
        self.courseDes = None
        self.username = None
        self.ownerId = None
        self.title = None
        self.parentId = None

    @staticmethod
    def sleep_print(sec):
        for i in range(sec):
            print(f"\r等待 {sec - i} 秒后继续", end='')
            time.sleep(1)

    def get(self, url, headers=None):
        while True:
            try:
                return self.Session.get(url, headers=headers)
            except:
                print("\r请求异常，重试中...")
                continue

    def post(self, url, post_json=None, headers=None):
        while True:
            try:
                return self.Session.post(url, json=post_json, headers=headers)
            except:
                print("\r请求异常，重试中...")
                continue

    def main(self) -> None:
        info = self.getInfomation()
        try:
            print('Login ID:', info['username'])
        except:
            input("xsid有误，请检查！")
            return
        self.ownerId = info['id']
        self.username = info['username']

        courseData = []
        for index, i in enumerate(self.getCourseInfo()['data']):
            print("{}、{}".format(index + 1, i['title']))
            courseData.append({
                "title": i['title'],
                "parentId": i['id'],
                "courseId": i['courseId']
            })
        while True:
            try:
                select_id = input('请选择课程（序号）:')
                self.title = courseData[int(select_id) - 1]['title']
                break
            except:
                select_id = None
                print("输入有误，请重新输入！")
                continue
        self.parentId = courseData[int(select_id) - 1]['parentId']
        self.courseId = courseData[int(select_id) - 1]['courseId']
        print("\n已选择 {}".format(self.title))

        while True:
            print("\n1、模拟观看网课\n2、题目作答（过期题目作答）\n3、题目作答（拷贝答案作答）\n4、导出题目与答案\n")
            select = input("请选择模式（序号）: ")
            autoCompletPapers = AutoCompletPapers(self.Session, self.courseId, self.title)
            if select == '1':
                self.CompleteCourse = self.getCompleteCourse()
                self.getCourseDes()
                self.startLearnCourse()
            elif select == '2':
                autoCompletPapers.sendAnswers(mode='due')
            elif select == '3':
                autoCompletPapers.sendAnswers()
            elif select == '4':
                print("\n1、从过期题目中导出\n2、从已作答的题目中导出\n")
                n = input("请选择模式（序号）: ")
                papersList = self.get(
                    f'https://www.cqooc.com/json/exam/papers?limit=200&start=1&courseId={self.courseId}&select=id,title&ts={getTs()}')

                papersIds = {}
                for i in papersList.json()['data']:
                    papersIds[i['id']] = i['title']
                if n == '1':
                    autoCompletPapers.saveAnswersFromDue(papersIds)
                elif n == '2':
                    autoCompletPapers.saveAnswersFromUser(papersIds)
                else:
                    print("输入有误，请重新输入！")
            elif select == '5':
                pass

            else:
                print("输入有误，请重新输入！")

    def getCourseDes(self):
        # 课程章节名
        self.Session.headers['Referer'] = f'https://www.cqooc.com/my/learn/mooc/structure?id={self.courseId}'
        courseDes = {}
        res = self.get(
            f'https://www.cqooc.com/json/chapters?limit=200&start=1&sortby=selfId&status=1&courseId={self.courseId}&select=id,title,level,selfId,parentId&ts={getTs()}')
        for i in res.json()['data']:
            courseDes[i['id']] = i['title']
        self.courseDes = courseDes

    def getInfomation(self) -> json:
        """
        获取基本信息
        :return:
        """
        return self.get('https://www.cqooc.com/user/session?xsid=' + cookie_xsid).json()

    def getCourseInfo(self) -> json:
        """
        获取课程信息
        :return:
        """
        self.Session.headers['Referer'] = 'https://www.cqooc.com/my/learn'
        return self.get(
            'https://www.cqooc.com/json/mcs?sortby=id&reverse=true&del=2&courseType=2&ownerId={}&limit=30'.format(
                self.ownerId)).json()

    def getCompleteCourse(self) -> list:
        """
        获取已完成小节列表
        :return:
        """
        # 防止死循环，最大能获取到的课程小节数为750（150*5），若实际课程小节数大于750，请将此值改大！
        maximumCycles = 5
        limit, start = 150, 1
        CourseIdList = []

        while True:
            maximumCycles -= 1

            self.Session.headers['Referer'] = 'https://www.cqooc.com/learn/mooc/progress?id=' + self.courseId
            data = self.get(
                f'https://www.cqooc.com/json/learnLogs?limit={limit}&start={start}&courseId={self.courseId}&select=sectionId&username={self.username}&ts={getTs()}',
                headers={
                    "referer": f'https://www.cqooc.com/learn/mooc/structure?id={self.courseId}'
                })

            learnLogs = data.json()['meta']

            for i in data.json()['data']:
                CourseIdList.append(i['sectionId'])

            # 课程未获取完全
            if len(CourseIdList) < int(learnLogs['total']):
                start += limit
            else:
                return CourseIdList
            if not maximumCycles:
                print("超出最大循环次数，若已完成小节未获取完全，请将 492 行值改大！")
                return CourseIdList

    def startLearn(self) -> json:
        self.Session.headers['Referer'] = 'https://www.cqooc.com/learn/mooc/structure?id=' + self.courseId
        return self.post(url='https://www.cqooc.com/account/session/api/login/time', post_json={
            "username": self.username
        }).json()

    def getLog(self, sectionId) -> json:
        self.Session.headers['Referer'] = 'https://www.cqooc.com/learn/mooc/structure?id=' + self.courseId
        return self.get(
            'https://www.cqooc.com/json/learnLogs?sectionId=' + sectionId + '&username=' + self.username).json()

    def checkProgress(self, courseId, sectionId, chapterId) -> None:
        count = 0
        while True:
            self.Session.headers['Referer'] = 'https://www.cqooc.com/learn/mooc/structure?id=' + courseId

            self.startLearn()
            self.getLog(sectionId)
            self.sleep_print(35)
            self.startLearn()
            time.sleep(1)

            Log = self.post('https://www.cqooc.com/learnLog/api/add', post_json={
                "action": 0,
                "category": 2,
                "chapterId": str(chapterId),
                "courseId": str(courseId),
                "ownerId": self.ownerId,
                "parentId": str(self.parentId),
                "sectionId": int(sectionId),
                "username": self.username
            })

            if count <= 2:
                date = 40
            else:
                date = 150

            try:
                if Log.json()['msg'] == '已经添加记录' or Log.json()['msg'] == 'No error':
                    return
                else:
                    self.sleep_print(date)
                    count += 1
                    continue
            except:
                continue

    def startLearnCourse(self):

        sectionList = \
            self.get('https://www.cqooc.com/json/chapter/lessons?courseId=' + self.courseId).json()['data'][0]['body']
        index_t = 0
        # CompleteCourse = self.getCompleteCourse()
        print("已完成小节数: {} ".format(len(self.CompleteCourse)))

        for chapterId, sectionIds in sectionList.items():
            print('\r章节进度: {}/{}({:.2f}%) \t当前: {}'.format(index_t + 1, len(sectionList.items()),
                                                                 ((float(
                                                                     (index_t + 1) / len(sectionList.items()))) * 100),
                                                                 self.courseDes.get(chapterId)))
            index_t += 1
            for index, sectionId in enumerate(sectionIds):
                print('\r\t小节进度: %d/%d(%.2f%%)' % (
                    index + 1, len(sectionIds), (float((index + 1) / len(sectionIds)) * 100)), end='')
                if sectionId in self.CompleteCourse:
                    print('\t已完成，跳过!')
                    continue
                print('\t成功!')
                self.checkProgress(self.courseId, sectionId, chapterId)


if __name__ == '__main__':
    AutoCompleteOnlineCourse().main()
