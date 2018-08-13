# !/usr/bin/python
# -*- coding: utf-8 -*-
#收集项目的commits    
#代码基于本地项目集获取commit
import git  #gitpython
from pipreqs import pipreqs
import re,os
import csv,datetime
import requests,json
log1=open('log(commits).txt','a+')
log2=open('log(candidates).txt','a+')
log3=open('log(problems).txt','a+')
log4=open('log(jishu).txt','a+')
REGEXP = [
        re.compile(r'^import\s(.+)$'),
        re.compile(r'^from\s((?!\.+).*?) import\s(?:.*)$')]
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
        print(Aname,'not here!')
        print(Aname, file=log3)
        log3.flush()
        return []
    if (os.path.isdir('D:\\HasReqs\\' + Bname)):
        repoB = git.Git('D:\\HasReqs\\' + Bname)
        dirnameB = 'D:\\HasReqs\\' + Bname
    elif (os.path.isdir('F:\\HasReqs\\' + Bname)):
        repoB = git.Git('F:\\HasReqs\\' + Bname)
        dirnameB = 'F:\\HasReqs\\' + Bname
    else:
        print(Bname,'not here!')
        print(Bname,file=log3)
        log3.flush()
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
        return(true_import)
    except Exception:
        return []

def getcommit(daydel,commitsfile):
    reader=csv.reader(open('GephiSidename.csv'))  #读入上下游项目信息
    for i,row_name in enumerate(reader):
        Aname=row_name[1]
        Bname=row_name[0]
        Auser=row_name[3]
        Buser = row_name[2]
        print(i,Bname, Aname)
        repoAB=isvalid(Aname,Bname)
        if(repoAB==[]):
            continue
        GitA=repoAB[0]
        GitB=repoAB[1]
        dirnameB=repoAB[2]
        loginfoB = GitB.log('--date=format:%Y-%m-%d %H:%M:%S', '--pretty=format:####%ad %an:%s', '--numstat')
        loginfoB = str(loginfoB).split('####')
        ##获取全部的B的commit历史
        last_dayB=datetime.datetime(2000,1,1,0,0,0)
        last_loginfoA=[]
        len_stard=len(loginfoB)
        print(i,Bname,Aname,len_stard,file=log1)  
        log1.flush()
        num=0
        num_relevant=0
        for commitB in list(loginfoB):
            if(commitB):
            list_commitsB=commitB.strip('\n').split('\n')
            #如果包含B更改的文件
            if(len(list_commitsB)>1 and len(list_commitsB[0].split(':'))>=4):
                flag_method1=0  #commit message
                flag_method2=0  #issue message
                flag_method3=0  #import关系
                #检查B此次是否提及了对A的更改支持
                raw_commitB = str(list_commitsB[0].split(':')[3]).lower()
                raw_Aname = str(Aname).lower() 
                if(raw_commitB.find(raw_Aname)!=-1): 
                     flag_method1=1
                ##issue message
                patternB=raw_commitB.split()
                closeIssue = ['close', 'closes', 'closed', 'fix', 'fixes',
                                'fixed', 'resolve', 'resolves', 'resolved','issue']
                for i, item in enumerate(patternB):
                    if item.startswith('#'):
                        if patternB[i - 1] in closeIssue: 
                            Id = item.strip('#').strip('.')
                            issueType = 'issues'
                        else:  
                            Id = item.strip('#').strip(')')
                            issueType = 'pull'
                        # 向网络发起一个request
                        res_tr = '<title>(.*?) · ' + Buser + '/' + Bname + ' · GitHub</title>'
                        try:
                            s = requests.get('https://github.com/' + Buser + '/' + Bname + '/' + issueType + '/' + Id)   
                            s.encoding = 'utf-8'
                            pattern = re.findall(res_tr, s.text, re.S)
                            if(pattern):   #如果pattern不为空
                                raw_issue=str(pattern).lower()
                                if(raw_issue.find(str(Aname).lower())!=-1):
                                      flag_method2=1
                        except:
                            print('requests wrong!')       
                #如果此次B的更改确实为了支持A
                #回溯查找相关A的更改
                if(flag_method1==1 or flag_method2==1):
                    num_relevant= num_relevant
                    dateB=list_commitsB[0].split()[0].split('-')
                    timeB=list_commitsB[0].split()[1].split(':')
                    datetimeB=datetime.datetime(int(dateB[0]),int(dateB[1]),int(dateB[2]),int(timeB[0]),int(timeB[1]),int(timeB[2]))
                    temp1 = '--since=' +str(datetimeB-datetime.timedelta(days=181))
                    temp2='--until='+str(datetimeB+datetime.timedelta(days=1))
                    loginfoA = GitA.log(temp1,temp2,'--date=format:%Y-%m-%d %H:%M:%S', '--pretty=format:####%ad %an:%s', '--numstat')
                    loginfoA= str(loginfoA).split('####')
                    files_changeB180=''
                    flag_change180=0
                    datetimeA180=datetime.datetime(2000,1,1,0,0,0)
                    messageA180=''
                    files_changeA180=''
                    for commitA in list(loginfoA):
                        if (commitA):
                            list_commitsA = commitA.strip('\n').split('\n')
                            dateA=list_commitsA[0].split()[0].split('-')
                            timeA = list_commitsA[0].split()[1].split(':')
                            datetimeA = datetime.datetime(int(dateA[0]), int(dateA[1]), int(dateA[2]),
                                                          int(timeA[0]), int(timeA[1]), int(timeA[2]))

                            
                            files_changeA=''  
                            flag_changeA=0
                            #判断A是否更改.py文件
                            for i in range(1, len(list_commitsA)):
                                file_list = list_commitsA[i].split()[2]  
                                if (file_list.endswith('.py')):
                                    flag_changeA=1
                                    pname = re.sub(r'/', r'\\', file_list)
                                    files_changeA=files_changeA+'#'+pname
                            if(flag_changeA==0): 
                                continue
                            files_changeB ='' 
                            timedel=datetime.timedelta(days=daydel)      
                            if (len(list_commitsA) > 1 and datetimeB>datetimeA):
                                if(datetimeB<(datetimeA+ timedel)):
                                    for i in range(1,len(list_commitsB)):
                                        file_list=list_commitsB[i].split()[2]  
                                        if (file_list.endswith('.py')):
                                            pname = re.sub(r'/', r'\\', file_list)
                                            filename = os.path.join(dirnameB, pname)
                                            true_imports = readPy(filename)
                                            #如果依赖非空，同时与A相关
                                            if true_imports: 
                                                for item in true_imports:   
                                                    if Aname==item.split('.')[0]:     
                                                        files_changeB = files_changeB + '#' + pname
                                    #与A相关的B在此次commit中更改的文件非空
                                    if (files_changeB): 
                                          flag_method3=1
                                          num=num+1
                                          timedelAB=(datetimeB-datetimeA)                                                         
                                          content = [Aname, Bname, files_changeA, files_changeB,datetimeA,datetimeB,
                                                     list_commitsA[0].split(':')[3],
                                                     list_commitsB[0].split(':')[3],
                                                    flag_method1,flag_method2,flag_method3,timedelAB]
                                          with open(commitsfile, 'a+', newline='') as csvfile:
                                                spamwriter = csv.writer(csvfile)
                                                spamwriter.writerow(content)
                                    #没有找到1天之内的，还没有第一次找到最近的A更改
                                if (flag_method3==0 and flag_change180==0 and datetimeB<(datetimeA+ datetime.timedelta(days=181))):
                                    datetimeA180=datetimeA
                                    files_changeA180=files_changeA
                                    messageA180=list_commitsA[0].split(':')[3]
                                    for i in range(1,len(list_commitsB)):
                                        file_list=list_commitsB[i].split()[2]  
                                        if (file_list.endswith('.py')):
                                            pname = re.sub(r'/', r'\\', file_list)
                                            filename = os.path.join(dirnameB, pname)
                                            true_imports = readPy(filename)
                                            if true_imports: 
                                                for item in true_imports:    
                                                    if Aname==item.split('.')[0]:     
                                                        files_changeB180 = files_changeB180 + '#' + pname
                                    if(files_changeB180):
                                        #那么就找到离B最近的一次的A的更改
                                        flag_change180=1    

                            
                    if(flag_method3==0):  
                        #如果一天之内没有相应的协同更改，那么就找到离B最近的一次的A的更改
                        if(files_changeB180):        
                          num=num+1
                          timedelAB=(datetimeB-datetimeA180)
                          print(timedelAB)  
                          content = [Aname, Bname, files_changeA180, files_changeB180,datetimeA180,datetimeB,
                                     messageA180,
                                     list_commitsB[0].split(':')[3],
                                    flag_method1,flag_method2,flag_method3,timedelAB]
                          with open(commitsfile, 'a+', newline='') as csvfile:
                                spamwriter = csv.writer(csvfile)
                                spamwriter.writerow(content)
        print(Bname,Aname,len_stard,num_relevant,num,file=log4)
        log4.flush()
getcommit(1,'commitsfinal.csv')    #1天




