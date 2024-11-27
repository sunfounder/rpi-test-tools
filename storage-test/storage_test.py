# 
# fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=read --name=read
# fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=write --name=write
# fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=randread --name=randread
# fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --filename=test --bs=4k --iodepth=64 --size=5G --readwrite=randwrite --name=randwrite


import subprocess
import argparse
import threading
import sys
import time
import json

TEST_FILE_NAME = "test"

TYPES = {
    "simple": [
        {'ioengine': 'libaio', 'rw': 'read', 'blocksize': '4k', 'queues': 64, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'write', 'blocksize': '4k', 'queues': 64, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randread', 'blocksize': '4k', 'queues': 64, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randwrite', 'blocksize': '4k', 'queues': 64, 'thread': 1},
    ],
    "hdd": [
        {'ioengine': 'libaio', 'rw': 'read', 'blocksize': '1M', 'queues': 8, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'read', 'blocksize': '1M', 'queues': 8, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'read', 'blocksize': '1M', 'queues': 1, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randread', 'blocksize': '4k', 'queues': 32, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randread', 'blocksize': '4k', 'queues': 1, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'write', 'blocksize': '1M', 'queues': 8, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'write', 'blocksize': '1M', 'queues': 1, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randwrite', 'blocksize': '4k', 'queues': 32, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randwrite', 'blocksize': '4k', 'queues': 1, 'thread': 1}
    ],
    "ssd": [
        {'ioengine': 'libaio', 'rw': 'read', 'blocksize': '1M', 'queues': 8, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'read', 'blocksize': '128K', 'queues': 32, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randread', 'blocksize': '4k', 'queues': 32, 'thread': 16},
        {'ioengine': 'libaio', 'rw': 'randread', 'blocksize': '4k', 'queues': 1, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'write', 'blocksize': '1M', 'queues': 8, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'write', 'blocksize': '128K', 'queues': 32, 'thread': 1},
        {'ioengine': 'libaio', 'rw': 'randwrite', 'blocksize': '4k', 'queues': 32, 'thread': 16},
        {'ioengine': 'libaio', 'rw': 'randwrite', 'blocksize': '4k', 'queues': 1, 'thread': 1}
    ]
}

msgs = {
    'en': {
        'read_write_modes_read': 'Read',
        'read_write_modes_randread': 'Random read',
        'read_write_modes_write': 'Write',
        'read_write_modes_randwrite': 'Random write',
        'type_error': 'Unsupported disk type: {type}, supported types: {supported_types}',
        'mode_error': 'Unsupported test mode: {mode}, supported modes: best/mean',
        'start_test': 'Disk speed test start. Press Ctrl+C to stop test.\n=====================\n  Test path: {path}\n  Value type: {type}\n  Test mode: {mode}\n  File size: {size}\n  Test times: {times}\n==========\n',
        'stop_test': 'Test stopped by user.',
        'language_error': 'Unsupported language: {language}, supported languages: en/zh',
        'mode_best': 'Best speed',
        'mode_mean':'Mean speed',
        'mode_trimed_mean': 'Trimed mean speed',
        'type_simple': 'Simple',
        'type_hdd': 'HDD',
        'type_ssd': 'SSD',
    },
    'zh': {
        'read_write_modes_read': '读',
        'read_write_modes_randread': '随机读',
        'read_write_modes_write': '写',
        'read_write_modes_randwrite': '随机写',
        'type_error': '不支持的磁盘类型：{type}, 支持的类型：{supported_types}',
        'mode_error': '不支持的测试模式：{mode}, 支持的模式：best/mean',
        'start_test': '磁盘测速开始。按 Ctrl+C 退出测速。\n=====================\n  测试路径：{path}\n  取值类型：{type}\n  测试模式：{mode}\n  文件大小：{size}\n  测试次数：{times}\n=====================\n',
        'stop_test': '测试已被用户终止。',
        'language_error': '不支持的语言：{language}, 支持的语言：en/zh',
        'mode_best': '最佳速度',
        'mode_mean': '平均速度',
        'mode_trimed_mean': '去极值平均',
        'type_simple': '简单',
        'type_hdd': '机械硬盘',
        'type_ssd': '固态硬盘',
    }
}
msg = None

parser = argparse.ArgumentParser(description='磁盘测速工具')
parser.add_argument('-l', '--language', type=str, default='zh', help='语言 (en/zh), 默认 zh')
parser.add_argument('-p', '--path', type=str, default=None, help='测试路径, 默认 ./')
parser.add_argument('-t', '--type', type=str, default='simple', help='测试类型 (simple/hdd/ssd), 默认 simple')
parser.add_argument('-s', '--size', type=str, default='5G', help='测试文件大小, 默认 5G')
parser.add_argument('-T', '--times', type=int, default=3, help='测试次数, 默认 3')
parser.add_argument('-m', '--mode', type=str, default='best', help='测试模式 (best/mean/trimed_mean), 默认 best')
args = parser.parse_args()

stop_spinner = True
spinner_message = ""

def get_rw_mode_string(name):
    if name == "read":
        return msg['read_write_modes_read']
    elif name == "randread":
        return msg['read_write_modes_randread']
    elif name == "write":
        return msg['read_write_modes_write']
    elif name == "randwrite":
        return msg['read_write_modes_randwrite']
    else:
        return name

def spin_indicator():
    while not stop_spinner:
        for character in "|/-\\":  # Spinner characters
            sys.stdout.write(f'\r{spinner_message} {character}')
            sys.stdout.flush()
            time.sleep(0.1)

def run_fio_command(command):
    global stop_spinner
    global spinner_message
    stop_spinner = False  # Reset the spinner before starting a new command
    spinner_thread = threading.Thread(target=spin_indicator)
    spinner_thread.start()

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        stop_spinner = True
        spinner_thread.join()
        return result
    except subprocess.CalledProcessError as e:
        stop_spinner = True
        spinner_thread.join()
        return f"Error: {e.output}"

def get_speed_from_json(json_str):
    result = None
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        print(f"JSON string: {json_str}")
        quit()
    job = data["jobs"][0]
    rw = job["job options"]["rw"]
    if "rand" in rw:
        rw = rw.replace("rand", "")

    result = job[rw]["bw_bytes"] / 1000 / 1000  # MB/s
    result = round(result, 2)
    return result

def create_fio_job(ioengine='libaio', blocksize='1M', thread=1, queues=1, rw='read'):
    name = f"{get_rw_mode_string(rw)}_{blocksize}_Q{queues}_T{thread}"
    command = f"fio --name={name} --filename={TEST_FILE_NAME} --gtod_reduce=1 --ioengine={ioengine} --size={{size}} --direct=1 --output-format=json --rw={rw} --bs={blocksize} --numjobs={thread} --iodepth={queues}"
    name = name.replace("_", " ")
    return name, command

def best_speed(speeds):
    return max(speeds)

def mean_speed(speeds):
    return round(sum(speeds) / len(speeds), 2)

def trimed_mean_speed(speeds):
    if len(speeds) < 3:
        return mean_speed(speeds)
    return round(sum(sorted(speeds)[1:-1]) / len(sorted(speeds)[1:-1]), 2)

def main():
    global stop_spinner, spinner_message, msg
    result = []
    test_path = "./"
    if args.path is not None:
        test_path = args.path

    if args.language not in msgs:
        print(msg['language_error'].format(language=args.language))
        exit(1)

    msg = msgs[args.language]

    if args.type not in TYPES:
        print(msg['type_error'].format(type=args.type, supported_types=", ".join(TYPES.keys())))
        exit(1)

    if args.mode == "best":
        func = best_speed
    elif args.mode == "mean":
        func = mean_speed
    elif args.mode == "trimed_mean":
        func = trimed_mean_speed
    else:
        print(msg['mode_error'].format(mode=args.mode))
        exit(1)

    print(msg['start_test'].format(path=test_path, type=msg[f"type_{args.type}"], mode=msg[f"mode_{args.mode}"], size=args.size, times=args.times))
    jobs = TYPES[args.type]
    for job in jobs:
        name, command = create_fio_job(**job)
        command = command.format(size=args.size)
        if args.path is not None:
            command += f" --directory={test_path}"
        # print(command)
        spinner_message = f"{name}:"
        print(f"{spinner_message} ", end='', flush=True)  # 先打印测试名称
        speeds = []
        speed = None
        for i in range(args.times):
            output = run_fio_command(command)
            speed = get_speed_from_json(output)
            speeds.append(speed)
            speed = func(speeds)
            spinner_message = f"{name}: {speed} MB/s ({i+1}/{args.times})"  # 打印测试进度
        
        stop_spinner = True  # 停止旋转指示
        result.append(speed)
        print(f"\r{name}: {speed} MB/s           ")
        sys.stdout.flush()

    print(",".join([str(speed) for speed in result]))

def delete_test_file():
    command = f"rm -f {TEST_FILE_NAME}"
    subprocess.run(command, shell=True)  # Remove test file

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(msg['stop_test'])
    finally:
        delete_test_file()
