import mysql.connector
from flask import Flask, request, jsonify
import cv2
import pytesseract
import requests
from config import DATABASE_CONFIG
import os
import re


# Tesseract 바이너리 파일 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 환경 변수 설정
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"


db = mysql.connector.connect(**DATABASE_CONFIG)
app = Flask(__name__)

# 텍스트 인식
def recognize_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(gray, lang='kor+eng')
    return text


def get_next_img_name():
    i = 1
    while True:
        img_name = f"img{i}.jpg"
        if not os.path.exists(f"images/{img_name}"):
            return img_name
        i += 1


def extract_text(text, keyword, pattern):
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None

def extract_ticket_info(text):
    seat = None
    location = None
    date_time = None

    # 좌석 정보 추출
    seat_match = re.search(r"(\d+)[^\d]+(\d+)[^\d]+(\d+)", text)
    if seat_match:
        floor = seat_match.group(1)
        row = seat_match.group(2)
        number = seat_match.group(3)
        seat = f"{floor}층 {row}열 {number}번"

    # 일시 정보 추출
    date_time_pattern = rf"일 시\s*[:：.]?\s*([\w\s]+)"
    date_time = extract_text(text, "일 시", date_time_pattern)

    # 장소 정보 추출
    location_pattern = rf"장 소\s*[:：.]?\s*([^\W\d_]+(?:\s+[^\W\d_]+)*)"
    location = extract_text(text, "장 소", location_pattern)

    return seat, location, date_time

@app.route('/api/v1/view-review/ticket', methods=['POST'])
def upload_ticket():
    
    # 클라이언트로부터 이미지 파일 받기
    ticket_file = request.files['ticket']

    # 이미지 파일 저장
    img_name = get_next_img_name()
    image_path = f"images/{img_name}"
    ticket_file.save(image_path)

    # 텍스트 추출
    text = recognize_text(image_path)

    # 티켓 정보 추출
    seat, location, date_time = extract_ticket_info(text)

    response = {
        '좌석': seat,
        '장소': location,
        '일시': date_time
    }

    return jsonify(response)


@app.route('/api/v1/view-review/ticket', methods=['PUT'])
def edit_ticket():

    edited_data = request.get_json()
    return jsonify(edited_data)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

