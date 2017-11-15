#!/usr/bin/env python
#! encoding=utf-8
#
# sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
#

import sys
import numpy as np

reload(sys)
sys.setdefaultencoding("utf-8")

class modelBuilder(object):
    def __init__(self):
        pass

    def get_name_of_chapter(self, index):
        if index < 10:
            return "00" + str(index)
        if index < 100:
            return "0" + str(index)
        return str(index)

    def get_name_of_chapter_wordfreq(self, index):
        return 'book/data/{0}_wordfrq.txt'.format(self.get_name_of_chapter(index))

    def get_wordnum_of_chapter(self, path):
        num = 0
        with open(path, 'r') as f:
            for line in f:
                words = line[:-1].split(' : ')
                num = num + int(words[1])
        return num

    def get_words_of_chapter(self, index):
        retults = []
        path = self.get_name_of_chapter_wordfreq(index)
        with open(path, 'r') as f:
            for line in f:
                words = line[:-1].split(' : ')
                retults.append(words[0])
        return retults

    #
    def get_common_words(self):
        # skip first and last chapter.
        common = self.get_words_of_chapter(1)
        for loop in range(2, 120):
            words = self.get_words_of_chapter(loop)
            common = list(set(common).intersection(set(words)))
        return common

    # 每个文档提取特征向量
    def build_feature_vector(self, index, label):
        path = self.get_name_of_chapter_wordfreq(index)
        total_words = self.get_wordnum_of_chapter(path)

        # common words in all chapters
        # function_word_list = ['有', '等', '不', '只', '便', '那', '听', '见',
        #                    '得', '又', '说', '在', '的', '到', '了', '是', '都'
        #                     ]
        function_word_list = ['了', '的', '在', '是', '便', '将', '把', '有', '却', '到', '等',
                           '只', '不', '里', '着', '要', '被', '正', '之', '罢', '自', '没',
                           '且', '个', '请', '已', '好', '一', '若', '并', '此', '为', '再'
                           '也', '又', '都', '得', '与', '和', '被', '就', '些', '但', '更', '尽', '休', '而',
                           '你', '我', '他', '那', '这', '这里', '这个',
                           '道', '来', '去', '说', '见', '听',
                           '上', '中', '下', '时', '待', '却是', '地'
                            ]
        feature_vector_list = []

        for function_word in function_word_list:
            find_flag = 0
            with open(path, 'r') as f:
                for line in f:
                    words = line[:-1].split(' : ')
                    if words[0] == function_word:
                        rate = float(words[1]) / total_words * 1000
                        rate = float("%.6f" % rate)# 指定位数
                        feature_vector_list.append(rate)
                        # print(words[0] + ' : ' + line)
                        find_flag = 1
                        break

            # 未找到词时向量为 0
            if not find_flag:
                feature_vector_list.append(0)

        feature_vector_list.append(label)
        return feature_vector_list

    def make_positive_trainset(self):
        positive_trainset_list = []
        for loop in range(40, 50):
            feature = self.build_feature_vector(loop, 1) #label 为 1 表示正例
            positive_trainset_list.append(feature)
        # print(positive_trainset_list)
        np.save('pos_trainset.npy', positive_trainset_list)

    def make_negative_trainset(self):
        negative_trainset_list = []
        for loop in range(90, 100):
            feature = self.build_feature_vector(loop, 2) #label 为 2 表示负例
            negative_trainset_list.append(feature)
        # print(negative_trainset_list)
        np.save('neg_trainset.npy', negative_trainset_list)

    def make_trainset(self):
        feature_pos = np.load('pos_trainset.npy')
        feature_neg = np.load('neg_trainset.npy')
        trainset = np.vstack((feature_pos, feature_neg))
        np.save('trainset.npy', trainset)

    def make_testset(self):
        testset_list = []
        for loop in range(0, 120):
            feature = self.build_feature_vector(loop, 0) #无需 label，暂设为 0
            testset_list.append(feature)
        # print(testset_list)
        np.save('testset.npy', testset_list)


def log_list(info, list):
    if info != '':
        print(info)
    for item in list:
        print('\'%s\', ' % (item))
    print("\n")

if __name__ == '__main__':
    builder = modelBuilder()

    # common = builder.get_common_words()
    # log_list("common words:", common)
    # print(builder.build_feature_vector(1))

    builder.make_positive_trainset()
    builder.make_negative_trainset()

    builder.make_trainset()
    builder.make_testset()
