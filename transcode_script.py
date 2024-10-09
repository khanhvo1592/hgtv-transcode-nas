import os
import time
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Đọc cấu hình từ file JSON
with open('config.json', 'r') as f:
    config = json.load(f)

input_dirs = config['input_dirs']
output_dirs = config['output_dirs']
log_file = config['log_file']
time_interval = config['time_interval']
days_old = config['days_old']

def load_converted_files(log_file):
    logging.info("Loading converted files from log.")
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            converted_files = f.read().splitlines()
    else:
        converted_files = []
    return set(converted_files)

def save_converted_file(log_file, file_name):
    logging.info(f"Saving converted file to log: {file_name}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(file_name + '\n')

def delete_old_files(directory, days_old):
    logging.info(f"Deleting old files in directory: {directory}")
    now = time.time()
    cutoff = now - (days_old * 86400)  # 86400 seconds in a day
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_creation_time = os.path.getctime(file_path)
            if file_creation_time < cutoff:
                os.remove(file_path)
                logging.info(f"Deleted {file_path}")

def convert_video(input_file, output_file, log_file):
    logging.info(f"Starting conversion for: {input_file}")
    command = [
        'ffmpeg', '-i', input_file, 
        '-vf', 'scale=1280:720,drawtext=fontfile=font.ttf:text=\'%{pts\\:hms}\':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10', 
        '-c:v', 'h264_nvenc', '-preset', 'fast', '-profile:v', 'main', '-b:v', '1M', 
        '-c:a', 'aac', '-b:a', '128k', 
        output_file
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        save_converted_file(log_file, os.path.basename(input_file))
        logging.info(f"Successfully converted: {input_file}")
    else:
        logging.error(f"Error converting {input_file}: {result.stderr}")

def process_directory(input_dir, output_dir, log_file, converted_files):
    logging.info(f"Processing directory: {input_dir}")
    if not os.path.exists(input_dir):
        logging.error(f"Input directory does not exist: {input_dir}")
        return

    tasks = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.mpg'):
                input_file = os.path.join(input_dir, file_name)
                output_file = os.path.join(output_dir, os.path.splitext(file_name)[0] + '.mp4')
                
                if not os.path.exists(output_file) and file_name not in converted_files:
                    logging.info(f"Submitting task for file: {file_name}")
                    task = executor.submit(convert_video, input_file, output_file, log_file)
                    tasks.append(task)
        
        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing file: {e}")

converted_files = load_converted_files(log_file)

while True:
    logging.info("Starting new processing cycle.")
    for input_dir, output_dir in zip(input_dirs, output_dirs):
        process_directory(input_dir, output_dir, log_file, converted_files)
        delete_old_files(output_dir, days_old)
    
    logging.info(f"Sleeping for {time_interval} seconds.")
    time.sleep(time_interval)