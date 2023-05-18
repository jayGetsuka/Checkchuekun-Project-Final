# ใช้งาน Python 3.8 เป็น base image
FROM python:3.8

#ติดตั้ง cmake 
RUN apt-get update && apt-get install -y cmake build-essential && apt-get install -y libgl1-mesa-glx

# ติดตั้ง pipenv
RUN pip install pipenv

# สร้างโฟลเดอร์ในเครื่อง host เพื่อใช้ในการ mount volume 
RUN mkdir /app
WORKDIR /app

# อ่าน pipfile และติดตั้ง dependency ที่ระบุไว้
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --ignore-pipfile

# อัปโหลด code ในโฟลเดอร์ /app
COPY . /app
COPY ANGSA.ttf /usr/share/fonts/truetype/

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
