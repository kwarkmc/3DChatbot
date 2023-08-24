import glob
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

import pyodbc

#Azure SQL DB Initialization 부분
server='tcp:sql-3dchatbot-server.database.windows.net,1433'
database='3D-ChatbotDB'
username='SKT1'
password=''

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password+';Encrypt=yes;TrustServerCertificate=no;')

cursor = conn.cursor()

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

        #./MOTION 폴더 내에 생성된 resultsanim0.bvh 파일을 읽어서 DB에 저장한다.
        bvh_path = './MOTION/resultsanim0.bvh'

        #rename bvh file
        try:
            #remove space in prompt
            prompt_processed = prompt.replace(' ', '')
            prompt_processed = prompt_processed.replace('.', '')
            print('PROMPT : ' + prompt)
            #print('BVH PATH : ' + bvh_path)
            os.rename(bvh_path, f'./MOTION/{prompt_processed}.bvh')
            bvh_path = f'./MOTION/{prompt_processed}.bvh'
            print(f"Renamed {bvh_path} to ./MOTION/{prompt_processed}.bvh")
        except OSError as e:
            print(f'파일 이름 변경 실패: {e}')

        bvh_name = bvh_path.split('/')[-1]
        print('BVH NAME : ' + bvh_name)

        data_to_insert = {
            'Timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            'MotionContent': prompt,
            'LabelName': 'test',
            'FileName': bvh_name,
            'FileData': open(bvh_path, 'rb').read()
        }

        insert_query = """
        INSERT INTO BVHdb (Timestamp, MotionContent, LabelName, FileName, FileData)
        VALUES (?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, list(data_to_insert.values()))

        conn.commit()

        print(f"Inserted {bvh_name} into the database")
    

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
    conn.close() #DB와 연결 종료

observer.join()

