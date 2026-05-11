from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import qrcode
from io import BytesIO
import base64

app = FastAPI()

# React 연결 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

NEIS_KEY = os.getenv("NEIS_KEY")


# -------------------------
# 🔎 자동완성 (구글 느낌)
# -------------------------
@app.get("/auto")
def auto(q: str):

    url = "https://open.neis.go.kr/hub/schoolInfo"

    res = requests.get(url, params={
        "KEY": NEIS_KEY,
        "Type": "json",
        "SCHUL_NM": q
    })

    try:
        rows = res.json()["schoolInfo"][1]["row"]
        return {"data": [r["SCHUL_NM"] for r in rows[:5]]}
    except:
        return {"data": []}


# -------------------------
# 🏫 학교 검색 + 이미지 + QR
# -------------------------
@app.get("/search")
def search(q: str):

    url = "https://open.neis.go.kr/hub/schoolInfo"

    res = requests.get(url, params={
        "KEY": NEIS_KEY,
        "Type": "json",
        "SCHUL_NM": q
    })

    try:
        rows = res.json()["schoolInfo"][1]["row"]

        result = []

        for r in rows:

            # 📱 QR 생성
            qr = qrcode.make(r["SCHUL_NM"])
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_b64 = base64.b64encode(buffer.getvalue()).decode()

            # 🖼 이미지 (랜덤 교실 이미지)
            img = f"https://source.unsplash.com/600x400/?school,classroom,{r['SCHUL_NM']}"

            result.append({
                "name": r["SCHUL_NM"],
                "address": r["ORG_RDNMA"],
                "office": r["ATPT_OFCDC_SC_NM"],
                "type": r["SCHUL_KND_SC_NM"],
                "img": img,
                "qr": qr_b64
            })

        return {"data": result}

    except:
        return {"data": []}
