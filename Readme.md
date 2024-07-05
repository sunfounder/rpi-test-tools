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
sudo apt-get install -y stress
sudo python3 -m pip install stressberry adafruit-circuitpython-dht --break-system-packages
```

### 测试

在树莓派GPIO链接一个DHT11传感器，3V3，GND，GPIO18（如果要修改引脚，就把下面的18给成你的引脚号）。

还要把.dat 改成合适的描述这个测试的名字。
把-n后面的名字改成描述这个测试的名称，名字会在导出的图表上显示。

```bash
stressberry-run -a 11 18 pironman-5-mini-fan-quiet-acrylic-open.dat -n "Pironman 5 Mini Fan Quiet Acrylic Open"
```

### 生成图表

```bash
stressberry-plot -d 300 --delta-t pironman-5-mini-fan-quiet-acrylic-open.dat -o pironman-5-gpio-fan-mode-0-off.png
``` 

### 多个数据合成一张图表
    
```bash
stressberry-plot -d 300 --delta-t \
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