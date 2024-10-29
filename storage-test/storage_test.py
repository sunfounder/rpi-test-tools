import subprocess
import argparse
import threading
import sys
import time
import json

lang = sys.argv[1] if len(sys.argv) > 1 else 'en'

msgs = {
    'en': {
        'description': 'Storage speed test',
        'lang_help': 'Language, default en, optional zh',
        'arg_path_help': 'Device path, like /mnt/sda1',
        'arg_type_help': 'Type of disk, like ssd or hdd',
        'arg_size_help': 'Size of test file, like 1G or 100M, default 1G',
        'arg_times_help': 'Number of test times, default 5',
        'arg_mode_help': 'Test mode, average or best, default average',
        'read_write_modes_read': 'Sequential read',
        'read_write_modes_randread': 'Random read',
        'read_write_modes_write': 'Sequential write',
        'read_write_modes_randwrite': 'Random write',
        'type_error': 'Unsupported disk type: {type}, supported types: {supported_types}',
        'mode_error': 'Unsupported test mode: {mode}, supported modes: best/average',
        'start_test': 'Disk speed test start, path: {path}. Press Ctrl+C to stop test.',
        'stop_test': 'Test stopped by user.'
    },
    'zh': {
        'description': '磁盘速度脚本',
        'lang_help': '语言，默认 en, 可选 zh',
        'arg_path_help': '设备路径，如 /mnt/sda1',
        'arg_type_help': '磁盘类型，如 ssd 或者 hdd',
        'arg_size_help': '测试文件大小，如 1G 或者 100M，默认 1G',
        'arg_times_help': '测试次数，默认 5',
        'arg_mode_help': '测试模式，平均average 或者 最佳best，默认 average',
        'read_write_modes_read': '顺序读',
        'read_write_modes_randread': '随机读',
        'read_write_modes_write': '顺序写',
        'read_write_modes_randwrite': '随机写',
        'type_error': '不支持的磁盘类型：{type}, 支持的类型：{supported_types}',
        'mode_error': '不支持的测试模式：{mode}, 支持的模式：best/average',
        'start_test': '磁盘测速开始，路径：{path}。按 Ctrl+C 退出测速。',
        'stop_test': '测试已被用户终止。'
    }
}
msg = msgs[lang]

parser = argparse.ArgumentParser(description=msg['description'])
parser.add_argument(lang, help=msg['description'])
parser.add_argument('-p', '--path', type=str, help=msg['arg_path_help'])
parser.add_argument('-t', '--type', type=str, help=msg['arg_type_help'])
parser.add_argument('-s', '--size', type=str, default='1G', help=msg['arg_size_help'])
parser.add_argument('-T', '--times', type=int, default=5, help=msg['arg_times_help'])
parser.add_argument('-m', '--mode', type=str, default='average', help=msg['arg_mode_help'])
args = parser.parse_args()

stop_spinner = True
spinner_message = ""

READ_WRITE_MODES = {
    "read": msg['read_write_modes_read'],
    "randread": msg['read_write_modes_randread'],
    "write": msg['read_write_modes_write'],
    "randwrite": msg['read_write_modes_randwrite']
}

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
    data = json.loads(json_str)
    job = data["jobs"][0]
    rw = job["job options"]["rw"]
    if "rand" in rw:
        rw = rw.replace("rand", "")

    result = job[rw]["bw_bytes"] / 1000 / 1000  # MB/s
    result = round(result, 2)
    return result

def create_fio_job(ioengine='libaio', blocksize='1M', thread=1, queues=1, rw='read'):
    name = f"{READ_WRITE_MODES[rw]}_{blocksize}_Q{queues}_T{thread}"
    command = f"sudo fio --name={name} --ioengine={ioengine} --directory={{path}} --size={{size}} --direct=1 --output-format=json --rw={rw} --bs={blocksize} --numjobs={thread} --iodepth={queues}"
    name = name.replace("_", " ")
    return name, command

COMMANDS = {
    "hdd": [
        create_fio_job(ioengine='libaio', rw='read', blocksize='1M', queues=8, thread=1),
        create_fio_job(ioengine='libaio', rw='read', blocksize='1M', queues=1, thread=1),
        create_fio_job(ioengine='libaio', rw='randread', blocksize='4k', queues=32, thread=1),
        create_fio_job(ioengine='libaio', rw='randread', blocksize='4k', queues=1, thread=1),
        create_fio_job(ioengine='libaio', rw='write', blocksize='1M', queues=8, thread=1),
        create_fio_job(ioengine='libaio', rw='write', blocksize='1M', queues=1, thread=1),
        create_fio_job(ioengine='libaio', rw='randwrite', blocksize='4k', queues=32, thread=1),
        create_fio_job(ioengine='libaio', rw='randwrite', blocksize='4k', queues=1, thread=1)
    ],
        "ssd": [
        create_fio_job(ioengine='libaio', rw='read', blocksize='1M', queues=8, thread=1),
        create_fio_job(ioengine='libaio', rw='read', blocksize='128K', queues=32, thread=1),
        create_fio_job(ioengine='libaio', rw='randread', blocksize='4k', queues=32, thread=16),
        create_fio_job(ioengine='libaio', rw='randread', blocksize='4k', queues=1, thread=1),
        create_fio_job(ioengine='libaio', rw='write', blocksize='1M', queues=8, thread=1),
        create_fio_job(ioengine='libaio', rw='write', blocksize='128K', queues=32, thread=1),
        create_fio_job(ioengine='libaio', rw='randwrite', blocksize='4k', queues=32, thread=16),
        create_fio_job(ioengine='libaio', rw='randwrite', blocksize='4k', queues=1, thread=1)
    ]
}

def main():
    global stop_spinner, spinner_message
    result = []
    test_path = "./"
    if args.path is not None:
        test_path = args.path

    if args.type not in COMMANDS:
        print(msg['type_error'].format(type=args.type, supported_types=", ".join(COMMANDS.keys())))
        exit(1)

    if args.mode == "best":
        func = max
    elif args.mode == "average":
        func = lambda x: round(sum(x) / len(x), 2)
    else:
        print(msg['mode_error'].format(mode=args.mode))
        exit(1)

    print(msg['start_test'].format(path=test_path))
    commands = COMMANDS[args.type]
    for name, command in commands:
        command = command.format(path=test_path, size=args.size)
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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(msg['stop_test'])
