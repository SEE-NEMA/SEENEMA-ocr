import mysql.connector
from flask import Flask, request
import cv2
import pytesseract
from config import DATABASE_CONFIG
import os

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

    return text

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)