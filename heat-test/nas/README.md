
```
stressberry-run -a ds18b20 4 nas.dat -n "NAS"
stressberry-run -a ds18b20 4 nas-small-heat-sink.dat -n "小散热片"

stressberry-plot -d 300 --delta-t \
nas.dat \
nas-small-heat-sink.dat \
-o nas-散热测试.png

```