#! encoding=utf-8
#!/usr/bin/python

import os

# scan
def scan_file(filepath, prefix, output_file):
    exclude_extends = ['.mp3', '.jpeg', '.jpg', '.db', '.txt', '.wma', '.nfo']
    path = filepath.lower()
    for extends in exclude_extends:
        if path.endswith(extends):
            return

    info = '\n{0}- {1}'.format(prefix, os.path.basename(filepath))
    output_file.write(info)
    # print(info)


def scan_dir(path, prefix, output_file):
    info = '\n{0}+ {1}'.format(prefix, os.path.basename(path))
    output_file.write(info)
    # print(info)

    prefix = '{0}    '.format(prefix)
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            # exclude hidden dirs
            if not filename.startswith('.'):
                scan_dir(filepath, prefix, output_file)
        elif os.path.isfile(filepath):
            scan_file(filepath, prefix, output_file)


def scan(path):
    output = 'result'
    if(os.path.isfile(output)):
        os.remove(output)
    output_file = open(output, 'a')

    prefix = ''
    if(os.path.isdir(path)):
        scan_dir(path, prefix, output_file)
    elif(os.path.isfile(path)):
        scan_file(path, prefix, output_file)
    output_file.close()

# rename
def rename_file(filepath, prefix, output_file):
    path = filepath.lower()
    if not path.endswith('.mp3'):
        return

    target = "宝宝睡前故事集---"
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    index = basename.find(target)
    if index != -1:
        basename = basename[index + len(target):]
        newpath = "{}/{}".format(dirname, basename)
        # print(" >> prev path: {}".format(filepath))
        # print(" >>  new path: {}".format(newpath))
        os.rename(filepath, newpath)

def rename_dir(path, prefix, output_file):
    info = '\n{0}+ {1}'.format(prefix, os.path.basename(path))
    output_file.write(info)
    # print(info)

    prefix = '{0}    '.format(prefix)
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            # exclude hidden dirs
            if not filename.startswith('.'):
                rename_dir(filepath, prefix, output_file)
        elif os.path.isfile(filepath):
            rename_file(filepath, prefix, output_file)

def rename(path):
    output = 'result'
    if(os.path.isfile(output)):
        os.remove(output)
    output_file = open(output, 'a')

    prefix = ''
    if(os.path.isdir(path)):
        rename_dir(path, prefix, output_file)
    elif(os.path.isfile(path)):
        rename_file(path, prefix, output_file)
    output_file.close()


#============================================================================#
scan_path = '/media/luozhaohui/BIGBABY/Movies'
rename_path = '/media/sf_D_DRIVE/Download/BaiduNetdisk/外语/中文/睡前故事/宝宝睡前故事一百首'

# scan(scan_path)
rename(rename_path)

# 输出文件示例如下：
# result
#    + 国内电影
#        + 我叫刘跃进
#            - 我叫刘跃进.rmvb
#        + 那山那人那狗
#            - 那山那人那狗.rmvb
#        + 大红灯笼高高挂
#            - 大红灯笼高高挂.rmvb
#        + 东邪西毒
#            - 东邪西毒.rmvb
#        + 平衡
#            - [平衡].ping.heng.2001.RMVB-cnjlp.tv.rmvb
#        + 租妻
#            - 租妻.rmvb
#        + 鸡犬不宁
#            - [鸡犬不宁].One.Foot.Off.The.Ground.2006.DVDSCR.XviD-CNXP.avi
