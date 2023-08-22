import glob
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


#watchdogs=3.0.0
#TEXT 폴더 내에 파일이 생성되면, 파일을 읽어서 motion을 생성하고, motion.npy를 생성한다.

model_path = './save/humanml_trans_enc_512/model000200000.pt'
output_dir = './MOTION'
num_repetitions = 1
input_text = './TEXT'

base_command = f"python -m sample.generate --model_path {model_path} --output_dir {output_dir} --num_repetitions {num_repetitions}"

print('READY TO GENERATE MOTION!!')

def new_file(event):
    if event.is_directory:
        return
    print("New file %s detected" % event.src_path)

    start_time = time.time()

    path = './TEXT/*.txt'
    file_list = glob.glob(path)

    for file_name in file_list:
        print(file_name)

        with open(file_name, 'r') as f:
            prompt = f.read().strip()
        
        os.system(f"{base_command} --input_text {file_name}")

        try:
            os.remove(file_name)
            print(f"Removed {file_name}")
        except FileNotFoundError:
            print(f"{file_name} not found")
        except Exception as e:
            print(f"Failed to remove {file_name} because of {e}")
    

event_handler = FileSystemEventHandler()
event_handler.on_created = new_file

folder_to_track = "./TEXT"
observer = Observer()
observer.schedule(event_handler, folder_to_track, recursive=True)

observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

