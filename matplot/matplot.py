#!/usr/bin/env python
#! encoding=utf-8
#
# sudo apt-get install python-matplotlib
# sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
#

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator, FuncFormatter

def make_axis():
    x1 = [1, 2, 3, 4, 5]# Make x, y arrays for each graph
    y1 = [1, 4, 9, 16, 25]
    x2 = [1, 2, 4, 6, 8]
    y2 = [2, 4, 8, 12, 16]

    plt.plot(x1, y1, 'r')# use pylab to plot x and y
    plt.plot(x2, y2, 'g')

    plt.title('Plot of y vs. x')# give plot a title
    plt.xlabel('x axis')# make axis labels
    plt.ylabel('y axis')

    plt.xlim(0.0, 9.0)# set axis limits
    plt.ylim(0.0, 30.)

    plt.savefig('axis.png')
    plt.show()# show the plot on the screen

def pi_formatter(x, pos):
    """
    比较罗嗦地将数值转换为以pi/4为单位的刻度文本
    """
    m = np.round(x / (np.pi/4))
    n = 4
    if m%2==0: m, n = m/2, n/2
    if m%2==0: m, n = m/2, n/2
    if m == 0:
        return "0"
    if m == 1 and n == 1:
        return "$\pi$"
    if n == 1:
        return r"$%d \pi$" % m
    if m == 1:
        return r"$\frac{\pi}{%d}$" % n
    return r"$\frac{%d \pi}{%d}$" % (m,n)

def make_axis_ex():
    x = np.arange(0, 4*np.pi, 0.01)
    y = np.sin(x)

    fig = plt.figure(figsize=(8,4))
    fig.patch.set_color("g")    # 属性背景颜色
    fig.canvas.draw()           # 属性修改之后更新显示

    plt.plot(x, y)
    ax = plt.gca()

    # 设置两个坐标轴的范围
    plt.ylim(-1.5,1.5)
    plt.xlim(0, np.max(x))

    # 设置图的底边距
    plt.subplots_adjust(bottom = 0.15)

    plt.grid() #开启网格

    # 主刻度为pi/4
    ax.xaxis.set_major_locator( MultipleLocator(np.pi/4) )

    # 主刻度文本用pi_formatter函数计算
    ax.xaxis.set_major_formatter( FuncFormatter( pi_formatter ) )

    # 副刻度为pi/20
    ax.xaxis.set_minor_locator( MultipleLocator(np.pi/20) )

    # 设置刻度文本的大小
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(16)

    # 刻度标签
    for label in ax.xaxis.get_ticklabels():
        label.set_color("yellow")
        label.set_rotation(45)
        label.set_fontsize(16)

    # 刻度线
    for line in ax.xaxis.get_ticklines():
        line.set_color("red")
        line.set_markersize(25)
        line.set_markeredgewidth(3)

    plt.savefig('axis_ex.png')
    plt.show()


def make_curve():
    t = np.arange(0.0, 1.01, 0.01)
    s = np.sin(2 * 2 * np.pi * t)

    plt.fill(t, s * np.exp(-5 * t), 'r')
    plt.grid(True)

    # save as png(jpeg, pdf, etc)
    plt.savefig('curve.png')
    plt.show()

def make_curve_ex():
    x = np.linspace(0, 10, 1000)
    y = np.sin(x)
    z = np.cos(x**2)

    plt.figure(figsize=(10, 6))
    # label : 给所绘制的曲线一个名字，此名字在图示(legend)中显示。
    # 只要在字符串前后添加"$"符号，matplotlib就会使用其内嵌的latex引擎绘制的数学公式。
    plt.plot(x, y, label="$sin(x)$", color="red", linewidth=2)
    plt.plot(x, z, "b--", label="$cos(x^2)$")   # "b--"指定曲线的颜色和线型
    plt.xlabel("Time(s)")
    plt.ylabel("Volt")
    plt.title("PyPlot First Example")
    plt.ylim(-1.2, 1.2)
    plt.legend()    # 显示图示

    plt.savefig('curve_ex.png')
    plt.show()

def make_scatter():
    if False:
        fig = plt.figure()
        ax = fig.add_subplot(2,1,1) # two rows, one column, first plot
        t = ax.scatter(np.random.rand(20), np.random.rand(20))

        plt.savefig('scatter_one.png')
        plt.show()
    else:
        # Use numpy to load the data contained in the file
        # 'fakedata.txt' into a 2-D array called data
        data = np.loadtxt('fakedata.txt')

        # plot the first column as x, and second column as y
        plt.plot(data[:, 0], data[:, 1], 'ro')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.xlim(0.0, 10.)

        plt.savefig('scatter_two.png')
        plt.show()

def make_pie():
    # make a square figure and axes
    plt.figure(1, figsize=(6, 6))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])

    labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
    fracs = [15, 30, 45, 10]

    explode = (0, 0.05, 0, 0)
    plt.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)
    plt.title('Raining Hogs and Dogs', bbox={'facecolor':'0.8', 'pad':10})
    plt.savefig('pie.png')
    plt.show()

def make_histograms():
    # make an array of random numbers with a gaussian distribution with
    # mean = 5.0
    # rms = 3.0
    # number of points = 1000
    data = np.random.normal(5.0, 3.0, 1000)

    # make a histogram of the data array
    plt.hist(data)

    # make plot labels
    plt.xlabel('data')

    plt.savefig('histograms.png')
    plt.show()

def randrange(n, vmin, vmax):
    '''
    Helper function to make an array of random numbers having shape (n, )
    with each number distributed Uniform(vmin, vmax).
    '''
    return (vmax - vmin) * np.random.rand(n) + vmin

def make_scatter3d():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    n = 100

    # For each set of style and range settings, plot n random points in the box
    # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
    for c, m, zlow, zhigh in [('r', 'o', -50, -25), ('b', '^', -30, -5)]:
        xs = randrange(n, 23, 32)
        ys = randrange(n, 0, 100)
        zs = randrange(n, zlow, zhigh)
        ax.scatter(xs, ys, zs, c=c, marker=m)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.savefig('scatter3d.png')
    plt.show()

if __name__ == '__main__':
    #make_axis()
    #make_axis_ex()
    #make_curve()
    #make_curve_ex()
    #make_scatter()
    #make_pie()
    #make_histograms()
    make_scatter3d()