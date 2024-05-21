# 测试

- [测试](#测试)
  - [散热测试](#散热测试)
    - [安装工具](#安装工具)
    - [测试](#测试-1)
    - [生成图表](#生成图表)
    - [多个数据合成一张图表](#多个数据合成一张图表)
  - [硬盘测试](#硬盘测试)
    - [fio](#fio)


## 散热测试
### 安装工具

```bash
sudo apt install stress
sudo python3 -m pip install stressberry --break-system-packages
```

### 测试

```bash
stressberry-run pironman-5-gpio-fan-mode-0-off.dat -n OFF
```

### 生成图表

```bash
stressberry-plot pironman-5-gpio-fan-mode-0-off.dat -o pironman-5-gpio-fan-mode-0-off.png
``` 

### 多个数据合成一张图表
    
```bash
stressberry-plot \
pironman-5-gpio-fan-mode-0-off.dat \
pironman-5-gpio-fan-mode-1-quiet.dat \
pironman-5-gpio-fan-mode-2-balanced.dat \
pironman-5-gpio-fan-mode-3-performance.dat \
pironman-5-gpio-fan-mode-4-always.dat \
-o pironman-5-gpio-fan-mode.png

stressberry-plot \
pironman-5-gpio-fan-mode-4-always.dat \
rpi-official.dat \
-o pironman-5-x-rpi-official.png
```


## 硬盘测试

### fio

```
fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=read --name=read
fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=write --name=write
fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=randread --name=randread
fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=randwrite --name=randwrite
```