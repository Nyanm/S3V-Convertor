# S3V-Convertor
A simple one-shop SDVX music convertor 简单的一站式SDVX音乐转换器


### ！！！请在根目录下放置ffmpeg.exe后食用！！！


## How it works

简单地把s3v文件重命名为wma文件后，通过ffmpeg转码为mp3，再打几个tag的小程序，顺便按照版本归了个类；版本更新后重新运行程序可以实现更新

## How to use

可以直接跑build出来的exe，也可以放在IDE里面跑

跑exe时，需要在根目录放置ffmpeg.exe，随后根据提示依次选择源文件夹（HDD那个）和目的文件夹，程序会一趟把所有曲子转换过去

跑代码时，除了以上的步骤外，记得把"test_mode"置1，不然软件工作路径会出错

## Why so slow

按理来说应该直接去给wma文件加tag和封面，但是没有（找不到）现成的库去实现，又懒得去造轮子，就转码为mp3凑活一下

按理来说应该用多线程写这种东西，但是多线程好麻烦，于是单线程嗯跑，跑一趟大概15min。绿皮代码，凑活用吧！
