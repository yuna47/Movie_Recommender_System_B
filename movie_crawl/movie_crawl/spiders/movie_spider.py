import re
import time
import scrapy
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MovieSpider(scrapy.Spider):
    name = "movie"
    allowed_domains = ["kobis.or.kr"]
    start_urls = ["https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"]

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)

    def closed(self, reason):
        self.driver.quit()

    def parse(self, response, **kwargs):
        global raw_img_url
        url = "https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"
        self.driver.get(url)

        # 페이지 로딩될 때까지 잠시 대기
        time.sleep(1)

        # 크롤링 전 필터링
        def click_btn(xpath):
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            btn.click()

        def load_item(xpath):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )

        # 검색 필터 '더보기' 버튼 클릭
        click_btn('//*[@id="content"]/div[3]/div[2]/a[1]')

        # 제작 상태 '개봉' 필터링
        click_btn('//*[@id="sPrdtStatStr"]')
        click_btn('//*[@id="mul_chk_det0"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 장르 제외 필터링
        click_btn('//*[@id="sGenreStr"]')
        load_item('//*[@id="tblChk"]')
        click_btn('//*[@id="chkAllChkBox"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det18"]')
        click_btn('//*[@id="mul_chk_det19"]')
        click_btn('//*[@id="mul_chk_det20"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 국적1(한국) 선택
        click_btn('//*[@id="sNationStr"]')
        click_btn('//*[@id="mul_chk_det2"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 국적2(한국) 선택
        click_btn('//*[@id ="sRepNationStr"]')
        click_btn('//*[@id="mul_chk_det2"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 등급 필터링
        click_btn('//*[@id="searchForm"]/div[2]/div[5]/div')
        # 2006-10-29~현재
        click_btn('//*[@id="mul_chk_det2"]')
        click_btn('//*[@id="mul_chk_det3"]')
        click_btn('//*[@id="mul_chk_det4"]')
        click_btn('//*[@id="mul_chk_det5"]')
        # 2002-05-01~2006-10-28
        click_btn('//*[@id="mul_chk_det10"]')
        click_btn('//*[@id="mul_chk_det11"]')
        click_btn('//*[@id="mul_chk_det12"]')
        click_btn('//*[@id="mul_chk_det13"]')
        # 2002-05-01~2006-10-28
        click_btn('//*[@id="mul_chk_det17"]')
        click_btn('//*[@id="mul_chk_det18"]')
        click_btn('//*[@id="mul_chk_det19"]')
        click_btn('//*[@id="mul_chk_det20"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 영화 종류 필터링
        click_btn('//*[@id="searchForm"]/div[2]/div[8]/div/label[2]')
        click_btn('//*[@id="searchForm"]/div[2]/div[8]/div/label[3]')
        time.sleep(1)

        # 필터링 후 검색
        click_btn('//*[@id="searchForm"]/div[1]/div[5]/button[1]')
        time.sleep(2)

        # 크롤링 시작
        click_btn('//*[@id="pagingForm"]/div/a[1]')
        time.sleep(1)
        for i in range(1, 8):
            click_btn('//*[@id="pagingForm"]/div/a[3]')
            time.sleep(1)

        # 페이지 순회
        while True:
            for page_number in range(1, 11):
                page_number_xpath = f'//*[@id="pagingForm"]/div/ul/li[{page_number}]'

                page_number_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, page_number_xpath))
                )
                page_number_link.click()

                # 페이지 로딩 대기
                time.sleep(1)

                # 각 페이지 테이블 내용 순회
                movie_rows = self.driver.find_elements(By.XPATH, '//*[@id="content"]/div[4]/table/tbody/tr')
                for idx, row in enumerate(movie_rows, start=1):
                    # '공연'과 '성인물(에로)'을 제외한 장르 필터링
                    genre_xpath = f'//*[@id="content"]/div[4]/table/tbody/tr[{idx}]/td[7]/span'
                    genre = self.driver.find_element(By.XPATH, genre_xpath).text
                    excluded_genres = ['공연', '성인물(에로)']
                    if any(excluded_genre in genre for excluded_genre in excluded_genres):
                        continue

                    # 모달 창 열기
                    movie_detail_xpath = f'//*[@id="content"]/div[4]/table/tbody/tr[{idx}]/td[1]/span/a'

                    movie_detail_link = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, movie_detail_xpath))
                    )
                    movie_detail_link.click()

                    # 시놉시스 가져오기
                    synopsis_xpath_1 = '/html/body/div[3]/div[2]/div/div[1]/div[5]/p'
                    synopsis_xpath_2 = '/html/body/div[3]/div[2]/div/div[1]/div[6]/p'
                    try:
                        synopsis = self.driver.find_element(By.XPATH, synopsis_xpath_1).text
                    except NoSuchElementException:
                        # 두 번째 XPath 시도
                        try:
                            synopsis = self.driver.find_element(By.XPATH, synopsis_xpath_2).text
                        # 없는 경우 크롤링 제외(모달창 닫기)
                        except NoSuchElementException:
                            close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                            self.driver.find_element(By.XPATH, close_btn).click()
                            continue

                    # 제목 가져오기
                    title_xpath = '/html/body/div[3]/div[1]/div[1]/div/strong'
                    try:
                        title = self.driver.find_element(By.XPATH, title_xpath).text
                    # 없는 경우 크롤링 제외(모달창 닫기)
                    except NoSuchElementException:
                        close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                        self.driver.find_element(By.XPATH, close_btn).click()
                        continue

                    # 감독 가져오기
                    director_xpath_1 = '/html/body/div[3]/div[2]/div/div[1]/div[6]/div/dl/div[1]/dd/a'
                    director_xpath_2 = '/html/body/div[3]/div[2]/div/div[1]/div[7]/div/dl/div[1]/dd/a'
                    try:
                        director = self.driver.find_element(By.XPATH, director_xpath_1).text
                    except NoSuchElementException:
                        # 두 번째 XPath 시도
                        try:
                            director = self.driver.find_element(By.XPATH, director_xpath_2).text
                        # 없는 경우 크롤링 제외(모달창 닫기)
                        except NoSuchElementException:
                            close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                            self.driver.find_element(By.XPATH, close_btn).click()
                            continue

                    # 배우 가져오기
                    actor_elements_1 = self.driver.find_elements(By.XPATH,
                                                               '/html/body/div[3]/div[2]/div/div[1]/div[6]/div/dl/div[2]/dd/table[1]/tbody/tr/td/a')
                    actor_elements_2 = self.driver.find_elements(By.XPATH,
                                                               '/html/body/div[3]/div[2]/div/div[1]/div[7]/div/dl/div[2]/dd/table[1]/tbody/tr/td/a')

                    actors_list = []
                    try:
                        for actor_element in actor_elements_1:
                            actor_info = actor_element.text.split('(')[0].strip()
                            # 배우의 이름만 가져오기
                            if '(' in actor_info:
                                actor_name = actor_info.split(' ')[-1].strip()
                            else:
                                actor_name = actor_info.strip()
                            actors_list.append(actor_name)
                    except NoSuchElementException:
                        pass
                    # 두 번째 XPath 시도
                    try:
                        for actor_element_2 in actor_elements_2:
                            actor_info = actor_element_2.text.split('(')[0].strip()
                            # 배우의 이름만 가져오기
                            if '(' in actor_info:
                                actor_name = actor_info.split(' ')[-1].strip()
                            else:
                                actor_name = actor_info.strip()
                            actors_list.append(actor_name)
                    # 둘 다 없는 경우 크롤링 제외(모달창 닫기)
                    except NoSuchElementException:
                        close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                        self.driver.find_element(By.XPATH, close_btn).click()
                        continue
                    actor = ', '.join(actors_list)

                    # 장르 가져오기
                    genre_info_xpath = '/html/body/div[3]/div[2]/div/div[1]/div[2]/dl/dd[4]'
                    try:
                        genre_info = self.driver.find_element(By.XPATH, genre_info_xpath).text
                        genre_pattern = re.compile(r'\|\s*[^|]+\s*\|\s*([^|]+)\s*\|')
                        match = genre_pattern.search(genre_info)
                        genre = match.group(1).strip()
                    # 없는 경우 크롤링 제외(모달창 닫기)
                    except NoSuchElementException:
                        close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                        self.driver.find_element(By.XPATH, close_btn).click()
                        continue

                    # 이미지 가져오기
                    img_xpath = '/html/body/div[3]/div[2]/div/div[1]/div[2]/a'
                    try:
                        img_element = self.driver.find_element(By.XPATH, img_xpath)
                        # alt 속성 가져오기
                        alt_attribute = img_element.get_attribute("alt")

                        # "이미지 없음"이 아닌 경우에만 원본 이미지 페이지로 이동(이미지 크롤링 수행)
                        if alt_attribute != "이미지 없음":
                            click_btn(img_xpath)

                            main_window_handle = self.driver.current_window_handle
                            # 원본 이미지 창의 핸들을 얻기
                            new_window_handles = [handle for handle in self.driver.window_handles if
                                                  handle != main_window_handle]
                            new_window_handle = new_window_handles[0]

                            # 원본 이미지 창으로 전환
                            self.driver.switch_to.window(new_window_handle)
                            raw_img_xpath = '/html/body/a/img'
                            raw_img_element = self.driver.find_element(By.XPATH, raw_img_xpath)
                            raw_img_url = raw_img_element.get_attribute("src")

                            # 원본 이미지 창에서의 작업이 완료되면 창을 닫기
                            self.driver.close()

                            # 기존의 창으로 전환
                            self.driver.switch_to.window(main_window_handle)

                    # 이미지가 없는 경우 크롤링 제외(모달창 닫기)
                    except NoSuchElementException:
                        close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                        self.driver.find_element(By.XPATH, close_btn).click()
                        continue

                    # 모달창 닫기
                    close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                    self.driver.find_element(By.XPATH, close_btn).click()

                    # 가져온 정보를 yield하여 Scrapy 아이템으로 전달
                    yield {
                        'title': title.strip(),
                        'genre': genre.strip(),
                        'director': director.strip(),
                        'actor': actor.strip(),
                        'synopsis': synopsis.strip(),
                        'img_url': raw_img_url
                    }

            # 페이지 넘기기 버튼 클릭
            try:
                click_btn('//*[@id="pagingForm"]/div/a[3]')
                time.sleep(1)
            except TimeoutException:
                # 다음 페이지 버튼이 없으면 종료
                self.driver.close()
                return
