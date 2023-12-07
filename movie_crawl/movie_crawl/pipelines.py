import csv
import codecs


class CsvPipeline:
    def __init__(self):
        self.file = codecs.open("output/movie.csv", 'w', encoding='utf-8-sig')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Title', 'Genre', 'Director', 'Actor', 'Synopsis', 'Img'])  # CSV 파일의 헤더

    def process_item(self, item, spider):
        title = item.get('title')
        genre = item.get('genre')
        director = item.get('director')
        actor = item.get('actor')
        synopsis = item.get('synopsis')
        img = item.get('img_url')

        # 각 데이터를 리스트로 만들어서 writerow에 전달
        self.writer.writerow([title, genre, director, actor, synopsis, img])

        return item

    def close_spider(self, spider):
        self.file.close()
