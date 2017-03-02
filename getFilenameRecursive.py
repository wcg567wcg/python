#! encoding=utf-8
#!/usr/bin/python

import os
import sys

def get_finename(path):
	filename = path
	index = path.rfind('/');
	if index != -1:
		filename = path[index+1:len(path)]
	return filename

def scan_file(filepath, prefix, output_file):
	exclude_extends = ['.mp3', '.jpeg', '.jpg', '.db', '.txt', '.wma', '.nfo']
	path = filepath.lower()
	for extends in exclude_extends:
		if path.endswith(extends):
			return

	info = '\n{0}- {1}'.format(prefix, get_finename(filepath))
	output_file.write(info)
	#print info

def scan_dir(path, prefix, output_file):
	info = '\n{0}+ {1}'.format(prefix, get_finename(path))
	output_file.write(info)
	#print info

	prefix = '{0}    '.format(prefix)
	listfile = os.listdir(path)
	for filename in listfile:
		filepath = path + '/' + filename
		if(os.path.isdir(filepath)):
			# exclude hidden dirs
			if(filename[0] != '.'):
				scan_dir(filepath, prefix, output_file)
		elif(os.path.isfile(filepath)):
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
		scan_file(filepath, prefix, output_file)
	output_file.close()

#===================================================================================#
scan_path = '/media/luozhaohui/BIGBABY/Movies'	

scan(scan_path)

# 输出文件示例如下：
#result
#	+ 国内电影
#		+ 我叫刘跃进
#			- 我叫刘跃进.rmvb
#		+ 那山那人那狗
#			- 那山那人那狗.rmvb
#		+ 大红灯笼高高挂
#			- 大红灯笼高高挂.rmvb
#		+ 东邪西毒
#			- 东邪西毒.rmvb
#		+ 平衡
#			- [平衡].ping.heng.2001.RMVB-cnjlp.tv.rmvb
#		+ 租妻
#			- 租妻.rmvb
#		+ 鸡犬不宁
#			- [鸡犬不宁].One.Foot.Off.The.Ground.2006.DVDSCR.XviD-CNXP.avi
