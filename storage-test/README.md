
# 硬盘测试

## fio

硬盘测试依赖于fio 安装：

```bash
sudo apt-get install fio -y
```

测试：
修改-p参数为需要测试的路径，比如/mnt/sda0。修改-t参数为hdd或ssd。

```bash
cd rpi-test-tools/storage-test
# 中文测试命令
sudo python3 storage_test.py
# 英文测试命令
```
