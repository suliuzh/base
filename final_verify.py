# !/usr/bin/python
# -*- coding: utf-8 -*-

#收集项目的commits
import git  #gitpython
from pipreqs import pipreqs
import re,os
import csv,datetime
import requests,json


log=open('temp.txt','a+')


REGEXP = [
        re.compile(r'^import\s(.+)$'),
        re.compile(r'^from\s((?!\.+).*?) import\s(?:.*)$')
    ]

res=re.compile(r'(\w|[_]|[-])+')


def isvalid(Aname,Bname):
    if (os.path.isdir('D:\\HasReqs\\' + Aname)):
        repoA = git.Git('D:\\HasReqs\\' + Aname)
    elif (os.path.isdir('D:\\HasnotReqs\\' + Aname)):
        repoA = git.Git('D:\\HasnotReqs\\' + Aname)
    elif (os.path.isdir('F:\\HasReqs\\' + Aname)):
        repoA = git.Git('F:\\HasReqs\\' + Aname)
    elif (os.path.isdir('F:\\HasnotReqs\\' + Aname)):
        repoA = git.Git('F:\\HasnotReqs\\' + Aname)
    else:
       # print(Aname,'not here!')
       # print(Aname, file=log3)
       # log3.flush()
        return []
    if (os.path.isdir('D:\\HasReqs\\' + Bname)):
        repoB = git.Git('D:\\HasReqs\\' + Bname)
        dirnameB = 'D:\\HasReqs\\' + Bname
    elif (os.path.isdir('F:\\HasReqs\\' + Bname)):
        repoB = git.Git('F:\\HasReqs\\' + Bname)
        dirnameB = 'F:\\HasReqs\\' + Bname
    else:
       # print(Bname,'not here!')
       # print(Bname,file=log3)
       # log3.flush()
        return []
    return [repoA,repoB,dirnameB]

def readPy(filename):
    try:
        file_object = open(filename, encoding='utf-8')
        file_content = file_object.readlines()
        imports = []
        for line in file_content:
            if (line.startswith('#')):
                continue
            for item in REGEXP:
                pattern1 = re.match(item, line)
                if (pattern1):
                    imports.append(pattern1.group())
        true_imports = []
        for content in imports:
            contents = str(content)
            strs = contents.split()
            if (contents.startswith('import')):
                true_imports.append(strs[1])
            else:
                true_imports.append(strs[1])
        true_import=[]
        candidates = pipreqs.get_pkg_names(true_imports)
        f=open('names.txt')
        data = [x.strip().split('\t') for x in f.readlines()]
        for pkg in candidates:
            toappend = pkg
            for item in data:
                if item[0] == pkg:
                    toappend = item[1]
                    break
            if toappend not in true_import:
                true_import.append(toappend)
       # print(true_import)
        return(true_import)
    except Exception:
        return []
        
        
        
def getcommit(daydel,commitsfile):
    reader=csv.reader(open('testname.csv'))
    try:
        for i,row_name in enumerate(reader):
                if(i<4):     
                    continue
                # if(i==10000):
                    # return None
                Aname=row_name[1]
                Bname=row_name[0]
                print(i,Bname, Aname)
                repoAB=isvalid(Aname,Bname)
                if(repoAB==[]):
                    continue
                GitA=repoAB[0]
                GitB=repoAB[1]
                dirnameB=repoAB[2]
                loginfoA = GitA.log('--date=format:%Y-%m-%d %H:%M:%S', '--pretty=format:####%ad %an:%s', '--numstat')
                loginfoA = list(str(loginfoA).split('####'))
                len_stard=len(loginfoA)
                #print(len_stard)
                ##因为时间是倒序的，所以前20%就是时间上靠后的20%
                len_limit=int(len_stard*0.1)
                commitA=loginfoA[len_limit]
                list_commitsA = commitA.strip('\n').split('\n')                     
                if(len(list_commitsA)>1):
                    list_commitsA = commitA.strip('\n').split('\n')
                    dateA=list_commitsA[0].split()[0].split('-')
                    timeA = list_commitsA[0].split()[1].split(':')
                    time_limit = datetime.datetime(int(dateA[0]), int(dateA[1]), int(dateA[2]),
                                                  int(timeA[0]), int(timeA[1]), int(timeA[2]))
                            
                #训练集，在time_limit之前的
                print(time_limit)
                list_files=[]   #排名信息对应的字典
                A_files=[]
                B_files=[]
                flag_begin=0
                finaldata=csv.reader(open('finaldata.csv'))
                for item in finaldata:
                    #print(item[0],Aname,item[1],Bname)
                    if(item[0]==Aname and item[1]==Bname):    #如果是对应的AB项目对
                        flag_begin=1
                        dateA=item[4].split()[0].split('/') #空格之前的是日期，只需要比较日期
                        timeA=datetime.datetime(int(dateA[0]),int(dateA[1]),int(dateA[2]))
                        #print(timeA)
                        if (timeA>time_limit): #如果时间上还是大于的
                            continue
                        else:   #建立训练集（即排名信息）
                            if(list_files):  #如果信息不为空
                                Afiles = str(item[2]).strip('#').split('#')
                                Bfiles = str(item[3]).strip('#').split('#')
                                for itemA in Afiles:
                                    for itemB in Bfiles:
                                        if itemA not in A_files:
                                            temp = [Aname,Bname,itemA, itemB, 1, 1]
                                            list_files.append(temp)
                                            A_files.append(itemA)
                                        elif itemB not in B_files:
                                            temp = [Aname,Bname,itemA, itemB, 1, 1]
                                            list_files.append(temp)
                                            B_files.append(itemB)
                                        else:
                                            for item in list_files:
                                                if(itemA==item[2] and itemB==item[3]):
                                                    item[4]=item[4]+1
                                                    item[5]=item[5]+1
                                                if(itemA==item[2] and itemB!=item[3]):
                                                    item[5] = item[5] + 1
                                
                            else:
                                Afiles=str(item[2]).strip('#').split('#')
                                Bfiles=str(item[3]).strip('#').split('#')
                                for itemA in Afiles:
                                    for itemB in Bfiles:
                                        if itemB not in B_files:
                                            B_files.append(itemB)
                                        if itemA not in A_files:
                                            A_files.append(itemA)
                                        temp=[Aname,Bname,itemA,itemB,1,1]
                                        list_files.append(temp)               
                    else:
                        if(flag_begin==1):  #指该段项目信息已完毕，整个break出来
                            break
                        else:
                            continue
                getlistfiles=[]  #这是A对应的B文件，此处我们先不考虑排名的方式，只考虑是否有预测正确，用键可能不对，因为键不能一样
                for item in list_files:
                    temp=[item[2],item[3]]
                    getlistfiles.append(temp)
                    content=[item[0],item[1],item[2],item[3],item[4],item[5],item[4]/item[5]]
                    with open('get_list1.csv', 'a+', newline='') as csvfile:
                        spamwriter = csv.writer(csvfile)
                        spamwriter.writerow(content)       
                    
                #print(getlistfiles)    
                #rank1(Aname,Bname,finaldata)
                #测验集
                for timei in range(len_limit):
                    commitA=loginfoA[len_limit-timei-1] #因为是倒序 
                    if(commitA): 
                        list_commitsA = commitA.strip('\n').split('\n')                     
                        if(len(list_commitsA)>1):
                            list_commitsA = commitA.strip('\n').split('\n')
                            dateA=list_commitsA[0].split()[0].split('-')
                            timeA = list_commitsA[0].split()[1].split(':')
                            datetimeA = datetime.datetime(int(dateA[0]), int(dateA[1]), int(dateA[2]),
                                                          int(timeA[0]), int(timeA[1]), int(timeA[2]))
                            
                            files_changeA=[]
                            files_predictB=[]
                            flag_changeA=0
                            flag_predictB=0
                            
                            for i in range(1, len(list_commitsA)):
                                file_list = list_commitsA[i].split()[2]  # 获取B更改的文件
                                if (file_list.endswith('.py')):
                                    pname = re.sub(r'/', r'\\', file_list)
                                    flag_changeA=1
                                    files_changeA.append(pname)
                                    for candidate in getlistfiles: 
                                        if(candidate[0]==pname):   #如果有A文件在的话
                                           files_predictB.append(candidate[1])#这就是预测的B更改文件
                           # print(files_changeA)
                           # print(files_predictB)
                           # return None
                            #如果B更改文件不为空，那么预测的就是发生了协同更改
                            if(files_predictB):
                                flag_predictB=1
                                      
                            #B在之后一天的更改，如果出现B提及A，那么真实情况就是发生了协同更改，同时要判断更改文件
                            #如果未出现B提及A，那么真实情况就是没有发生协同更改
                            flag_true_predict=0
                            files_true_predict=[]
                            files_update=[]
                            
                            flag_method1=0  #commit message
                            flag_method2=0  #issue message
                            flag_method3=0  #import关系
                
                            if(flag_changeA==1):
                                temp1 = '--since=' +str(datetimeA) 
                                temp2='--until='+str(datetimeA+datetime.timedelta(days=2)) 
                                loginfoB = GitB.log(temp1,temp2,'--date=format:%Y-%m-%d %H:%M:%S', '--pretty=format:####%ad %an:%s', '--numstat')
                                ##获取B的全部更改
                                loginfoB= str(loginfoB).split('####')
                                #print(len(list(loginfoB)))
                                #print(list(loginfoB))
                                #return None
                               # return None
                                files_changeB =[] #与A相关的B在此次commit中更改的文件
                                for commitB in list(loginfoB):
                                    if(commitB):
                                        list_commitsB=commitB.strip('\n').split('\n')
                                        #如果包含B更改的文件
                                        if(len(list_commitsB)>1 and len(list_commitsB[0].split(':'))>=4):
                                            #检查B此次是否提及了对A的更改支持（commit message，issue message）
                                            raw_commitB = str(list_commitsB[0].split(':')[3]).lower()
                                            raw_Aname = str(Aname).lower()
                                            #单个单词的检验，更为准确，单个单词的元素有字母，下划线，连字符.，字母（现在先不搞了。。）
                                            flag_highrelevant = raw_commitB.find(raw_Aname)
                                            if(flag_highrelevant!=-1):
                                                  flag_method1=1
                                            #print(flag_method1)
                                            if(flag_method1==1 or flag_method2==1):    #真实情况是发生了协同更改
                                                dateB=list_commitsB[0].split()[0].split('-')
                                                timeB=list_commitsB[0].split()[1].split(':')
                                                datetimeB=datetime.datetime(int(dateB[0]),int(dateB[1]),int(dateB[2]),int(timeB[0]),int(timeB[1]),int(timeB[2]))
                                                
                                                timedel=datetime.timedelta(days=1)
                                                if (datetimeB>datetimeA and datetimeB<(datetimeA+ timedel)):
                                                    for i in range(1,len(list_commitsB)):
                                                        file_list=list_commitsB[i].split()[2]  #获取B更改的文件
                                                        if (file_list.endswith('.py')):
                                                            pname = re.sub(r'/', r'\\', file_list) 
                                                            if pname not in files_changeB:
                                                                files_changeB.append(pname)
                                #本次协同更改的B的所有实际更改文件
                                if (files_changeB): #与A相关的B在此次commit中更改的文件非空
                                    #print(files_changeA)
                                    if(flag_predictB==1):
                                        flag_true_predict=1  #正确预测了会发生协同更改
                                        for Bfile in files_changeB:
                                            if Bfile in files_predictB:
                                               files_true_predict.append(Bfile)
                                            else:
                                                filename = os.path.join(dirnameB, Bfile)
                                                true_imports = readPy(filename)
                                                if true_imports: #如果依赖非空，同时与A相关
                                                    for dep in true_imports:    #保留了具体更改的文件格式
                                                        if Aname==dep.split('.')[0]:     
                                                           files_update.append(Bfile)
                                                           
                                    print(Aname,Bname,flag_true_predict,len(files_true_predict),len(files_predictB),len(files_changeB),len(files_true_predict)/len(files_changeB))
                                    #print(files_update)
                                    if (files_update): #如果有更新的情况
                                        for Afile in files_changeA:
                                            for Bfile in files_update:
                                                temp=[Afile,Bfile]
                                                getlistfiles.append(temp)
                                else:
                                    if(flag_predictB==0):
                                        flag_true_predict=1   #正确地预测了不会发生协同更改
                                   # print(Aname,Bname,flag_true_predict)              
                                       
                                                         
    finally:
        #os.popen('shutdown -s')
        print('all done!')

getcommit(1,'commitsfinal.csv')    #1周
#getcommit(90,'commits90.csv')     #3个月
#getcommit(180,'commits180.csv')    #6个月



