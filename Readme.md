# 测试

- [测试](#测试)
  - [散热测试](#散热测试)
    - [安装工具](#安装工具)
    - [测试](#测试-1)
    - [生成图表](#生成图表)
    - [多个数据合成一张图表](#多个数据合成一张图表)


## 散热测试
### 安装工具

```bash
sudo apt-get install -y python3-pip python3-dev stress git
sudo pip3 install git+https://github.com/sunfounder/stressberry --break-system-packages
sudo python3 -m pip install adafruit-circuitpython-dht --break-system-packages
```

### 测试

在树莓派GPIO链接一个DHT11传感器，3V3，GND，GPIO18（如果要修改引脚，就把下面的18给成你的引脚号）。
或者链接一个DS18B20，连GPIO4.

DS18B20需要在Raspi config 里面打开1-wire

可以先试试DHT11 能不能正常工作：
```bash
sudo python3 rpi-test-tools/test/dht11-test.py -p 18 -m dht11
```

或者试试DS18B20能不能正常工作
```bash
sudo python3 rpi-test-tools/test/ds18b20-test.py
```

开始测试，记得把.dat 改成合适的描述这个测试的名字。
把-n后面的名字改成描述这个测试的名称，名字会在导出的图表上显示。

```bash
stressberry-run -a 11 18 pironman-5-mini-fan-quiet-acrylic-open.dat -n "Pironman 5 Mini Fan Quiet Acrylic Open"
stressberry-run -a ds18b20 4 pironman-5-mini-fan-quiet-acrylic-open.dat -n "Pironman 5 Mini Fan Quiet Acrylic Open"
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

