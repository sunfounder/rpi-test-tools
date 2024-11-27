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
        'mode_error': 'Unsupported test mode: {mode}, supported modes: best/average',
        'start_test': 'Disk speed test start, path: {path}. Press Ctrl+C to stop test.',
        'stop_test': 'Test stopped by user.',
        'language_error': 'Unsupported language: {language}, supported languages: en/zh',
    },
    'zh': {
        'read_write_modes_read': '读',
        'read_write_modes_randread': '随机读',
        'read_write_modes_write': '写',
        'read_write_modes_randwrite': '随机写',
        'type_error': '不支持的磁盘类型：{type}, 支持的类型：{supported_types}',
        'mode_error': '不支持的测试模式：{mode}, 支持的模式：best/average',
        'start_test': '磁盘测速开始，路径：{path}。按 Ctrl+C 退出测速。',
        'stop_test': '测试已被用户终止。',
        'language_error': '不支持的语言：{language}, 支持的语言：en/zh',
    }
}
msg = None

parser = argparse.ArgumentParser(description='磁盘测速工具')
parser.add_argument('-l', '--language', type=str, default='zh', help='语言 (en/zh), 默认 zh')
parser.add_argument('-p', '--path', type=str, default=None, help='测试路径, 默认 ./')
parser.add_argument('-t', '--type', type=str, default='simple', help='测试类型 (simple/hdd/ssd), 默认 simple')
parser.add_argument('-s', '--size', type=str, default='1G', help='测试文件大小, 默认 5G')
parser.add_argument('-T', '--times', type=int, default=5, help='测试次数, 默认 1')
parser.add_argument('-m', '--mode', type=str, default='average', help='测试模式 (best/average), 默认 average')
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
        func = max
    elif args.mode == "average":
        func = lambda x: round(sum(x) / len(x), 2)
    else:
        print(msg['mode_error'].format(mode=args.mode))
        exit(1)

    print(msg['start_test'].format(path=test_path))
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
