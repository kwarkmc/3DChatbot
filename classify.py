from konlpy.tag import Kkma
import json

#chercker에는 어미를 저장해야 함. '아이들이 자주 사용할만한 단어의 어간', '저장할 bhv파일명', 영향력
checker = {
    '안녕' : ('hello.bvh',10),
    '점프' : ('jump.bvh',11),
    '배고프' : ('stomach.bvh',8),
    '뭐하' : ('shakehand.bvh',100),
}

kkma = Kkma()
Input_text = "우어어아아" ##사용자 입력 텍스트
Inputword_list = kkma.pos(Input_text)
Dict = {}
for i in range(len(Inputword_list)):
    slicedword = Inputword_list[i][0] 
    if slicedword not in Dict:
        Dict[slicedword] = 1
    else:
        Dict[slicedword] += 1
        
detected = []
for word in Dict:
    if word in checker:
        detected.append(checker[word])
detected.sort(key=lambda x:x[1], reverse=True)

print(detected)

if len(detected) > 0:
    print("서버에 미리 저장할 bvh이름을 분류기에 저장된 것으로 변경", "분류기에 저장된 bvh이름 : "+str(detected[0][0]), sep='\n')
    print("서버에 실제 저장된 bvh이름 :", None)
    #여기에 서버에 미리 저장된 bvh를 로컬 컴퓨터 폴더로 보내는 코드 적기
if len(detected) == 0:
    print("이 경우 미리 저장된bvh를 사용하지 않고 mdm으로 생성(기존 방식)")
    #여기에 mdm으로 bvh만들라고 지시하는 코드
print("입력텍스트 분석결과 ",Dict)

####################################################################################################
# 6세~10대초반 채팅 데이터셋이 있다면 아래 코드를 통해 Dict에 들어갈 단어들을 선정할 수도 있음
# All_path = "C:/Users/054/Downloads/2020-02-024.한국어SNS_sample/sample.json"
# All_path_2 = "C:/Users/054/Downloads/2020-02-020.한국어대화요약_sample/sample.json"
# with open(All_path, 'r', encoding='utf-8') as file:
#     data = json.load(file)
# count_all_data = len(data['data'])

# class Get_Specific_Info_From_Data():
#     def __init__(self) -> None:
#         pass
#     def GetHeadInfo(self, datanum):
#         return(data['data'][datanum]['header'])
#     def GetBodyInfo(self, datanum):
#         return(data['data'][datanum]['body'])
# GetInfo = Get_Specific_Info_From_Data()

# for i in range(count_all_data):
#     nowhead = GetInfo.GetHeadInfo(datanum = i)
#     nowbody = GetInfo.GetBodyInfo(datanum = i)
#     if nowhead['dialogueInfo']['numberOfParticipants'] == 2:
#         for j in range(len(nowbody)):
#             if nowhead["participantsInfo"][0]["age"] == "20대 미만" and nowhead["participantsInfo"][1]["age"] == "20대 미만":
#                 print(nowbody[j]['utterance'])
# T = {}
# for i in range(count_all_data):
#     nowhead = GetInfo.GetHeadInfo(datanum = i)
#     agetype = nowhead["participantsInfo"][0]["age"]
#     if agetype not in T:
#         T[agetype] = 1
#     else:
#         T[agetype] += 1
# print("나이대 : ", T)