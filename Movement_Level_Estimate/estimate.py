import numpy as np

file_path = "C:/Users/054/Desktop/xyzdata/They raise their right arm to demonstrate the motion of holding a squash racket.npy"
#T2M이 뱉어낸 motion.npy 파일의 저장 경로

Loaded_npy = np.load(file_path)[0] #Loaded_npy의 형태 : (프레임 수, 관절0번~21번, xyz좌표정보)
now_joints_pos = Loaded_npy[0] #now_joints_pos에 먼저 첫 번째 프레임의 관절 위치정보를 저장. 초기 위치 (관절0번~21번, xyz좌표정보)
distances = [0 for i in range(22)] # 관절 별로 한 프레임이 움직일때마다 이동된 거리를 더함


for frame in Loaded_npy: #데이터의 프레임 별로
    for i in range(len(frame)): #데이터의 관절 별로
        nowjoint = frame[i] #i번쨰 관절의 x,y,z 좌표
        prev = now_joints_pos[i] #바로 한 프레임 전 i번째 관절의 x,y,z 좌표
        distances[i] += ((nowjoint[0]-prev[0])**2 + (nowjoint[1]-prev[1])**2 + (nowjoint[2]-prev[2])**2)**0.5 
        #14번째 라인은 현재 프레임 관절 위치-직전 프레임 관절 위치를 매 프레임마다 계속 더함. 따라서 distances에는 각 관절의 모든 움직임 정보가 이 프레임 단위로 더해진다 
        now_joints_pos[i] = frame[i] #다음 루프에서 prev역할을 하게 한다. 
print(int(sum(distances))) # distances리스트에 저장된 각 관절들의 움직임 정도를 모두 더하고 정수로 리턴한다