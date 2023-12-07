import csv
from PIL import Image
from io import BytesIO
import requests

def resize_and_save_image(image_url, output_path, target_size=(200, 300), quality=95):
    try:
        # 이미지 URL에서 이미지를 가져옴
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # 원본 이미지 크기 확인
        original_size = image.size

        # 가로, 세로 중에서 더 긴 쪽을 기준으로 축소 비율 계산
        base_ratio = max(target_size[0] / original_size[0], target_size[1] / original_size[1])

        # 축소 비율을 적용하여 새로운 크기 계산
        new_size = (int(original_size[0] * base_ratio), int(original_size[1] * base_ratio))

        # 이미지 리사이즈
        resized_image = image.resize(new_size, resample=Image.LANCZOS)

        # 크기가 목표치를 초과하는 경우, 목표 크기로 다시 리사이즈
        resized_image = resized_image.resize(target_size, resample=Image.LANCZOS)

        # 리사이즈된 이미지를 저장
        resized_image.save(output_path, quality=quality)

        print(f"Resized and saved image to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

def index():
    # CSV 파일 읽기
    input_csv = './movie_crawl/output/movie2.csv'  # 원본 이미지 포함 csv
    output_csv = './movie_crawl/output/movie.csv'
    with open(input_csv, 'r', encoding='utf-8-sig') as infile, open(output_csv, 'w', newline='', encoding='utf-8-sig') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames  # 새로운 필드 추가하지 않음

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in enumerate(reader, start=1):
            # 각 행의 이미지 URL과 저장할 경로를 지정
            image_url = row['img']
            output_path = f"./static/image_resized/{index}.jpg"  # 행의 순서에 따른 인덱스 사용

            # 이미지 리사이즈 및 저장
            resize_and_save_image(image_url, output_path)

            # 이미 있는 'img' 필드의 값을 새로운 경로로 갱신
            row['img'] = output_path

            # 새로운 행을 CSV 파일에 추가
            writer.writerow(row)

index()