# CqoocAutoCompleteCourse
重庆高校在线刷课脚本

#### Python版本

+ 推荐 Python3 (3.6 - 3.8.1)

#### 已有功能
  - [x] 自动观看课程
  - [x] 课程选择
  - [x] 自动跳过已完成章节
  - [x] 自动答题
      - [x] 已过期题目作答（成绩可能无效，待测）
      - [x] 复制另一个用户的答案自动作答


**注：自动观看课程中不会自动做题！但学习进度依旧会显示完成，请自行完成小节习题！**

#### 依赖库安装

`pip install requests`

#### 使用方法

+ 首先登录重庆高校在线
+ 登录成功后，F12调出开发者工具 复制cookie中`xsid`的值
+ ![image](https://raw.githubusercontent.com/HirokiChin/CqoocAutoCompleteCourse/master/img/png2.png)
+ 然后替换掉文件中`cookie_xsid`的值
+ ![image](https://raw.githubusercontent.com/HirokiChin/CqoocAutoCompleteCourse/master/img/png3.png)
+ 保存，运行

#### 运行图
![image](https://raw.githubusercontent.com/HirokiChin/CqoocAutoCompleteCourse/master/img/png1.png)

### 自动答题说明

+ 过期题目作答
  + 即自动作答已过期的题目（需确保已过期的题目能够看到答案）
  + 提交后可能无分数，待测
  + ![image](https://tva1.sinaimg.cn/large/0081Kckwly1gl8pcrlqlgj30al033t8t.jpg)
+ 拷贝答案作答
  + 拷贝别人已作答题目的答案，来提交自己的（需提交已作答账户的cookie）

## 声明

+ **脚本仅供学习交流，严禁用于商业用途！**
+ **刷课有风险， 请合理使用脚本。**
