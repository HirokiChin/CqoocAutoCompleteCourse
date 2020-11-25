import requests
import time
import json

################### Config #############################

cookie_xsid = '' 

########################################################

class AutoCompleteOnlineCourse:
    def __init__(self) -> None:

        # headers
        session = requests.Session()
        session.headers['Cookie'] = 'player=1; xsid=' + cookie_xsid
        session.headers['Connection'] = 'close'
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        session.headers['Host'] = 'www.cqooc.net'
        self.Session = session
        self.CompleteCourse = None
        self.courseId = None
        self.courseDes = None

    def main(self) -> None:
        info = self.getInfomation()
        try:
            print('Login ID:', info['username'])
        except:
            print("xsid有误，请检查！")
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
                id = input('请选择课程（序号）:')
                self.title = courseData[int(id) - 1]['title']
                break
            except:
                print("输入有误，请重新输入！")
                continue
        self.parentId = courseData[int(id) - 1]['parentId']
        self.courseId = courseData[int(id) - 1]['courseId']
        print("\n已选择 {}\n".format(self.title))
        self.CompleteCourse = self.getCompleteCourse()
        self.getCourseDes()
        self.startLearnCourse()

    def getCourseDes(self):
        # 课程章节名
        self.Session.headers['Referer'] = f'http://www.cqooc.net/my/learn/mooc/structure?id={self.courseId}'
        courseDes = {}
        res = self.Session.get(f'http://www.cqooc.com/json/chapters?limit=200&start=1&sortby=selfId&status=1&courseId={self.courseId}&select=id,title,level,selfId,parentId&ts={int(round(time.time() * 1000))}')
        for i in res.json()['data']:
            courseDes[i['id']] = i['title']
        self.courseDes = courseDes

    def getInfomation(self) -> json:
        """
        获取基本信息
        :return:
        """
        return self.Session.get('http://www.cqooc.net/user/session?xsid=' + cookie_xsid).json()

    def getCourseInfo(self) -> json:
        """
        获取课程信息
        :return:
        """
        self.Session.headers['Referer'] = 'http://www.cqooc.net/my/learn'
        return self.Session.get(
            'http://www.cqooc.net/json/mcs?sortby=id&reverse=true&del=2&courseType=2&ownerId={}&limit=10'.format(
                self.ownerId)).json()

    def getCompleteCourse(self) -> list:
        """
        获取已完成小节列表
        :return:
        """
        self.Session.headers['Referer'] = 'http://www.cqooc.net/learn/mooc/progress?id=' + self.courseId
        data = self.Session.get(
            f'http://www.cqooc.com/json/learnLogs?limit=100&start=1&courseId={self.courseId}&select=sectionId&username={self.username}&ts={int(round(time.time() * 1000))}')
        CourseIdList = []
        for i in data.json()['data']:
            CourseIdList.append(i['sectionId'])
        return CourseIdList

    def startLearn(self) -> json:
        self.Session.headers['Referer'] = 'http://www.cqooc.net/learn/mooc/structure?id=' + self.courseId
        return self.Session.post(url='http://www.cqooc.net/account/session/api/login/time', json={
            "username": self.username
        }).json()

    def getLog(self, sectionId) -> json:
        self.Session.headers['Referer'] = 'http://www.cqooc.net/learn/mooc/structure?id=' + self.courseId
        return self.Session.get(
            'http://www.cqooc.net/json/learnLogs?sectionId=' + sectionId + '&username=' + self.username).json()

    def checkProgress(self, courseId, sectionId, chapterId) -> None:
        count = 0
        while True:
            self.Session.headers['Referer'] = 'http://www.cqooc.net/learn/mooc/structure?id=' + courseId

            self.startLearn()
            self.getLog(sectionId)
            time.sleep(20)
            self.startLearn()
            time.sleep(1)

            Log = self.Session.post('http://www.cqooc.net/learnLog/api/add', json={
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

            if Log.json()['msg'] == '已经添加记录' or Log.json()['msg'] == 'No error':
                return
            else:
                time.sleep(date)
                count += 1
                continue

    def startLearnCourse(self):

        sectionList = \
            self.Session.get('http://www.cqooc.net/json/chapter/lessons?courseId=' + self.courseId).json()['data'][0]['body']
        index_t = 0
        # CompleteCourse = self.getCompleteCourse()
        print("已完成小节数: {} ".format(len(self.CompleteCourse)))
        for chapterId, sectionIds in sectionList.items():
            print('章节进度: {}/{}({:.2f} \t当前: {}'.format(index_t + 1, len(sectionList.items()),
                                                        ((float((index_t + 1) / len(sectionList.items()))) * 100),
                                                        self.courseDes.get(chapterId)))
            index_t += 1
            for index, sectionId in enumerate(sectionIds):
                print('\t小节进度: %d/%d(%.2f%%)' % (
                    index + 1, len(sectionIds), (float((index + 1) / len(sectionIds)) * 100)), end='')
                if sectionId in self.CompleteCourse:
                    print('\t已完成，跳过!')
                    continue
                print('\t成功!')
                self.checkProgress(self.courseId, sectionId, chapterId)


if __name__ == '__main__':
    AutoCompleteOnlineCourse().main()
