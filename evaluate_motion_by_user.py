# 유저가 입력한 텍스트가 모션으로 잘 생성되어 실행됐는지 유저가 버튼을 눌러 평가하고, 평가 데이터를 bvh파일 이름으로 라벨링해서 DB에 저장하는 로직

# 서버에서 돌아가는 로직

# 1. 시작상태 버튼 OFF -> 
# 2. 서버에서 bvh 로컬로 보내면 앱에 명령전달(버튼 OFF -> 1초대기 -> 버튼 ON) -> 
# 3. 유저가 평가버튼을 누르면 서버에 명령전달(보냈던 bvh파일명을 'amanisjumping_85점'형태로 수정,평가데이터를 저장하는DB로 전송) ->
# 4. 앱 버튼 OFF -> 2.를 대기 

# 1. 시작상태 버튼 OFF -> 
# 2. 서버에서 bvh 로컬로 보내면 앱에 명령전달(버튼 OFF -> 1초대기 -> 버튼 ON) -> 
# 3. 유저가 평가버튼을 안누르고 대기하면 ->
# 4. 2.를 대기 

Score = None
flag = False
while True:
    if 서버에서 bvh 로컬로 보내서 flag true이면: 
        flag false
        앱의 평가버튼 off 
        1초 대기
        평가버튼 on 
        while True:
            if 앱에서 매우 정확함 버튼 누르면:
                Score = 100
            elif 앱에서 정확함 버튼 누르면:
                Score = 75
            elif 앱에서 보통임 버튼 누르면:
                Score = 50
            elif 앱에서 부정확함 버튼 누르면:
                Score = 25
            elif 앱에서 매우 부정확함 버튼 누르면:
                Score = 0
                
            if Score != None: #눌렀다면
                mdminput = gpt가 뱉은 프롬프트 결과값
                mdminput = list(mdminput)
                for i in range(len(mdminput)):
                    if mdminput[i].isalpha() == False:
                        mdminput[i] = "0"
                mdminput = "".join(mdminput) #gpt가 뱉은 문장에 알파벳 외의 것이 있다면 '0'으로 바꿔넣음
                프롬프트를 통해 생성한 bvh파일명을 'amanisjumping'+str(Score)로 수정
                평가데이터를 저장하는DB로 전송
                앱의 평가버튼 off 
                break
   
        
        