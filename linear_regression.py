#编程基础实在太差，花了好几天才看懂推荐的代码，请见谅，这次只能学习一下这个代码了，自己添加了一些注释




#!/usr/bin/env python 3.6
#-*- coding:utf-8 -*-
# @File    : LR_Gradient.py
# @Date    : 2019-03-03
# @Author  : 黑桃
# @Software: PyCharm 

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 读取文件


path = "D:/PM2.5/"
train = pd.read_csv(path + 'train.csv', engine='python', encoding='gbk')
test = pd.read_csv(path + 'test.csv', engine='python', encoding='gbk')

# 数据预处理删去不要的特征

##################提取有用的特征PM2.5相关的，去除非数据的列，，，dataframe切片要用.iloc

train = train[train['observation'] == 'PM2.5']
test = test[test['AMB_TEMP'] == 'PM2.5']
train = train.drop(['Date', 'stations', 'observation'], axis=1)
test_x = test.iloc[:, 2:]

# 使用训练集构成一个大的训练集
# 每连续的9列作为一组特征，后面的一列作为label，
# 原始数据就可以构造出15组这样的特征+label，最后拼接起来就是3600*9

##################制作训练数据集，包括特征和标签，每八个特征和一个标签对应，，，，15*（12*20天）=3600行数据，
##################此时train_x是15个（240,9）的dataframe组成的list，train_y是15个（240，）的series组成的list
train_x = []
train_y = []
for i in range(15):
    x = train.iloc[:, i:i + 9]
    x.columns = np.array(
        range(9))  # notice if we don't set columns name, it will have different columns name in each iteration
    y = train.iloc[:, i + 9]
    y.columns = np.array(range(1))
    train_x.append(x)
    train_y.append(y)

# pd拼接
##################train_x变为（3600,9）的dataframe，train_y变为（3600，）的series
train_x = pd.concat(train_x)
train_y = pd.concat(train_y)

##################train_y，test_x变为数组浮点形式
train_y = np.array(train_y, float)
test_x = np.array(test_x, float)
print(train_x.shape, train_y.shape)

# 数据归一化，若不归一化，数据收敛特别慢
##################归一化train_x，和test_x
ss = StandardScaler()
ss.fit(train_x)
train_x = ss.transform(train_x)

ss.fit(test_x)
test_x = ss.transform(test_x)

# 定义一个评价函数
##################np.sum
def r2_score(y_true, y_predict):
    """计算y_true和y_predict之间的MSE"""
    MSE = np.sum((y_true - y_predict) ** 2) / len(y_true)
    """计算y_true和y_predict之间的R Square"""
    return 1 - MSE / np.var(y_true)


# 线性回归，【参考某大佬的代码】

class LinearRegression:

    def __init__(self):
        """初始化Linear Regression模型"""
        self.coef_ = None
        self.intercept_ = None
        self._theta = None
##################这个函数好像没用到
    def fit_normal(self, X_train, y_train):
        """根据训练数据集X_train, y_train训练Linear Regression模型"""
        assert X_train.shape[0] == y_train.shape[0], \
            "the size of X_train must be equal to the size of y_train"

        X_b = np.hstack([np.ones((len(X_train), 1)), X_train])
        self._theta = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y_train)

        self.intercept_ = self._theta[0]
        self.coef_ = self._theta[1:]

        return self
##################训练过程
    def fit_gd(self, X_train, y_train, eta=0.01, n_iters=1e4):
        '''

        :param X_train: 训练集
        :param y_train: label
        :param eta: 学习率
        :param n_iters: 迭代次数
        :return: theta
        '''

        """根据训练数据集X_train, y_train, 使用梯度下降法训练Linear Regression模型"""
        assert X_train.shape[0] == y_train.shape[0], \
            "the size of X_train must be equal to the size of y_train"

        '''定义一个损失函数'''
        def J(theta, X_b, y):
            try:
                return np.sum((y - X_b.dot(theta)) ** 2) / len(y)
            except:
                return float('inf')
        '''对损失函数求导'''
        def dJ(theta, X_b, y):
            return X_b.T.dot(X_b.dot(theta) - y) * 2. / len(y)
##################梯度下降   按公式来的
        def gradient_descent(X_b, y, initial_theta, eta, n_iters=1e4, epsilon=1e-8):
            '''

            :param X_b:
            :param y: lebel
            :param initial_theta: 初始theta值
            :param eta: 学习率
            :param n_iters: 迭代次数
            :param epsilon: theta更新变化值
            :return:
            '''
            theta = initial_theta
            cur_iter = 0

            while cur_iter < n_iters:
                gradient = dJ(theta, X_b, y)
                last_theta = theta
                theta = theta - eta * gradient
                ##################如果loss变化小于epsilon值则停止
                if (abs(J(theta, X_b, y) - J(last_theta, X_b, y)) < epsilon):
                    break

                cur_iter += 1

            return theta
##################np.hstack水平方向粘接起来，w和b作为theta一起优化
        X_b = np.hstack([np.ones((len(X_train), 1)), X_train])


        initial_theta = np.zeros(X_b.shape[1])
        self._theta = gradient_descent(X_b, y_train, initial_theta, eta, n_iters)

        self.intercept_ = self._theta[0]
        self.coef_ = self._theta[1:]

        return self
##################给出预测值
    def predict(self, X_predict):
        """给定待预测数据集X_predict，返回表示X_predict的结果向量"""
        assert self.intercept_ is not None and self.coef_ is not None, \
            "must fit before predict!"
        assert X_predict.shape[1] == len(self.coef_), \
            "the feature number of X_predict must be equal to X_train"

        X_b = np.hstack([np.ones((len(X_predict), 1)), X_predict])
        return X_b.dot(self._theta)
##################打分
    def score(self, X_test, y_test):
        """根据测试数据集 X_test 和 y_test 确定当前模型的准确度"""

        y_predict = self.predict(X_test)
        return r2_score(y_test, y_predict)

    def __repr__(self):
        return "LR()"


##################返回一个类  LR
# 模型训练+评分+预测
LR = LinearRegression().fit_gd(train_x, train_y)
##################打分加预测
LR.score(train_x, train_y)
result = LR.predict(test_x)

# 保存结果
sampleSubmission = pd.read_csv(path + 'sampleSubmission.csv', engine='python', encoding='gbk')
sampleSubmission['value'] = result
sampleSubmission.to_csv(path + 'result.csv')
