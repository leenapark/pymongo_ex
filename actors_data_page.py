import requests as req
from bs4 import BeautifulSoup as bs
import pymongo


conn = pymongo.MongoClient('mongodb://localhost:27017')

# movies DB생성
movies = conn.movies

# actors_info 컬렉션 생성
actors_info = movies.actors_info

cine21_url = "http://www.cine21.com/rank/person/content" # post netword url

start_month = "2023-04"
url_de = "http://www.cine21.com/"

page_num = input("수집할 페이지를 입력하세요.")


# post network 에서 가져온 옵션값 저장
cdts = {}
cdts["section"] = "actor"
cdts["period_start"] = start_month
cdts["gender"] = "all"
cdts["page"] = page_num

res = req.post(cine21_url, data=cdts)

soup = bs(res.text, "html.parser")
docsList = [] # 전체 리스트
actor_li = soup.select(".people_list .people_li")
for actor in actor_li:
    actor_info_doc={}
    # print(actor)
    # 배우 이름
    name = actor.select_one(".name").get_text(strip=True).split("(")[0]
    # print(name)
    
    # 배우 이름 a 태그 href 속성값 url
    actor_url = actor.select_one(".name a").attrs["href"]
    actor_url = url_de + actor_url
    # print(actor_url)
    
    # 흥행 지수 : int 형으로 바꿈
    indices = actor.select_one(".tit+strong").get_text(strip=True).replace(",", "")
    # print(indices)
    
   
    
    # 배우의 상세 페이지
    actor_link = actor_url
    res_sub = req.get(actor_link)
    soup_sub = bs(res_sub.text, "html.parser")
    
    info_area = soup_sub.select(".default_info_area .default_info li")
    
    actor_info_dict = {}
    homepList = []
    for info in info_area:
        homepage = info.select("li a")
        # 기본 정보
        if info.select_one("li span+a") == None:
            key = info.select_one("li span.tit").get_text(strip=True)
            value = info.strings # list 로 넘겨줌
            value = list(value)[1]
            actor_info_dict[key] = value

        # 홈페이지
        for home in homepage:
            homepage = home.attrs["href"]
            homepList.append(homepage)
        actor_info_dict["홈페이지"] = homepList



    part_work = soup_sub.select("ul.part_works li")
    workList = [] # 참여 작품
    for work in part_work:
        # 영화 링크
        movie_link = work.select_one("li a").attrs["href"]
        movie_link = url_de + movie_link

        # 영화 제목
        work_name = work.select_one("span.tit").get_text(strip=True)

        # 개봉년도
        work_year = work.select_one("span.year").get_text(strip=True)

        workList.append([movie_link, work_name, work_year])
# print(actor_info_dict)
# print(workList)
    
    

    # 한 배우에 대한 data부터 만들어보기 : dict()

    actor_info_doc["actor"] = name
    actor_info_doc["actor_url"] = actor_url
    actor_info_doc["indices"] = indices
    actor_info_doc["start_period"] = start_month
    actor_info_doc["info"] = actor_info_dict
    actor_info_doc["movie_list"] = workList

    # print(actor_info_doc)
    # print("-"*30)
    docsList.append(actor_info_doc)
print(docsList)

actors_info.insert_many(docsList)

for doc in actors_info.find():
    print(doc)