# -*- coding:utf-8
#如何整合信息进行推荐
import re,csv
from sklearn import model_selection
from sklearn import tree
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.externals.six import StringIO
import pydot
import pydotplus   #这是为了write_pdf
import numpy
from sklearn.linear_model.logistic import LogisticRegression
import numpy as np
def simple_commend():
    csv_re=csv.reader(open('pandas_self.csv'))
    log_reccommend=open('files_reccommend.txt','a',encoding='utf-8')
    project_dict=[]
    count_yes=0
    count_no=0
    for i,row in enumerate(csv_re):
        issue1=row[0]
        authors_issue1 = row[1].split('#')
        files_issue1=row[2]
        issue2=row[3]
        project_name = issue2.split('#')[0]  #因为前者知道，所以只记录后者名称
        authors_issue2 = row[4].split('#')
        files_issue2 = row[5]
        issue_cos=row[6]
        commit_cos = row[7]
        if (files_issue1):    #如果files_issue1有就应该产生推荐
                    #if files_issue2:
                     #   print(files_issue2)
                    file1=files_issue1.split('#')
                    file_predict=[]
                    for file in file1:
                        for item in project_dict:
                            if file in item[0].split('#'):    #好蠢啊，如果存在过原来的数据库中，则进行推荐
                                for file_item in item[2].split('#'):
                                    if file_item:
                                        import_num = file_item.split(':')[1]
                                        if int(import_num) > 0:  #如果有import语句，才会推荐
                                            file_predict.append([item[1], file_item])
                    if(file_predict):
                        for file_ in  file_predict:
                           # print(row[0], '推荐了', file_[0], file_[1], file=log_reccommend)
                            if file_[1].split(':')[0] in list(map(lambda x: x.split(':')[0], files_issue2.split('#'))):  # 除非此次推荐的，是本次issue涉及的文件
                                print('yes! is right')
                                print(row[0], '推荐了', file_[0], file_[1])
                                count_yes += 1
                            else:
                                count_no +=1      #如果此次推荐的文件，并没有发生更改
                    #else:
                      #  if(files_issue2):
                      #      count_no +=1
                      #  else:
                        #    print('yes! is kong')
                        #    count_yes +=1
        if float(issue_cos)>0 and float(commit_cos)>0:   #如果相关
            if set(authors_issue1) & set(authors_issue2):   #如果开发者之间有交集
                if files_issue1 and files_issue2:
                    project_dict.append([files_issue1, project_name, files_issue2])    #意味着当满足条件才会推荐，所以成功的概率会高一点
    print(count_yes,count_no)
def tree_commend():
    #对数据进行预处理
    array=np.zeros((249,3))  #author,issue,commit
    array_result=np.zeros((249,1))
    csv_re = csv.reader(open('pandas_self.csv'))
    for i,row in enumerate(csv_re):
        issue1 = row[0]
        authors_issue1 = row[1].split('#')
        files_issue1 = row[2]
        issue2 = row[3]
        project_name = issue2.split('#')[0]  # 因为前者知道，所以只记录后者名称
        authors_issue2 = row[4].split('#')
        files_issue2 = row[5]
        issue_cos = row[6]
        commit_cos = row[7]
        author=set(authors_issue1) & set(authors_issue2)
        if author:
            array_result[i, 0] = 1
            if len(author)>2:
                array[i,0]=3
            else:
                array[i, 0] = len(author)
            if float(issue_cos) > 0:
                array[i, 1] = 1
                if float(commit_cos) > 0:
                    array[i, 2] = 1
                else:
                    array[i, 2] = 0
                    array_result[i, 0] = 0
            else:
                array[i, 1] = 0
                array_result[i, 0] = 0
        else:
            array[i,0]=0
            array_result[i, 0] = 0

    array_train,array_test,array_result_train,array_result_test=train_test_split(array,array_result,test_size=0.3,random_state=0)  #划分训练集和测试集，后面那个指每次随机情况不一样
    clf=tree.DecisionTreeClassifier(criterion="entropy")
    clf_model=clf.fit(array_train,array_result_train)
    print(clf.predict(array_test))
    print(clf.score(array_test,array_result_test))
    dot_data=StringIO()  #这是向本地打印的IO流
    tree.export_graphviz(clf_model,out_file=dot_data)
    graph =pydot.graph_from_dot_data(dot_data.getvalue())
    graph[0].write_pdf('image.pdf')
def DN_commend():
    array_files=[]
    array_result=[]
    file_dict={}
    num=1
    csv_re = csv.reader(open('matplotlib.csv'))
    for i, row in enumerate(csv_re):
        file1=row[2].split('#')
        file2=row[5].split('#')
        for file in file1:
            if file:
                for file_2 in file2:
                    if file_2:
                        file1_num=file_dict.get(file.split(':')[0],None)
                        file2_num=file_dict.get(file_2.split(':')[0],None)
                        if file1_num and file2_num:
                            array_files.append([file1_num,file2_num])
                        else :
                            if file1_num:
                                array_files.append([file1_num, num])
                                file_dict[file_2.split(':')[0]]=num
                                num+=1
                            elif file2_num:
                                array_files.append([num,file2_num])
                                file_dict[file.split(':')[0]]=num
                                num+=1
                            else:
                                array_files.append([num, num+1])
                                file_dict[file.split(':')[0]]=num
                                file_dict[file_2.split(':')[0]]=num+1
                                num+=2
                        array_result.append(1)

    #logistic regression
    array_filesMat=np.mat(array_files)
    array_resultMat=np.mat(array_result).transpose()
    array_train,array_test,array_result_train,array_result_test=train_test_split(array_filesMat,array_resultMat)  #划分训练集和测试集，后面那个指每次随机情况不一样
    Cs = np.logspace(-2, 4, num=100)
    scores = []
    for c in Cs:
        cls=LogisticRegression(C=c)
        cls.fit(array_train,array_result_train)
        #scores.append(cls.score(array_test, array_result_test))
        print(cls.score(array_test, array_result_test))
#tree_commend()
#simple_commend()
DN_commend()