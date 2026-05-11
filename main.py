from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# CORS (React 연결용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 환경변수
NEIS_KEY = os.getenv("NEIS_KEY")


# -----------------------------
# 안전한 학교 검색 함수
# -----------------------------
def get_school(name: str):

    url = "https://open.neis.go.kr/hub/schoolInfo"

    res = requests.get(url, params={
        "KEY": NEIS_KEY,
        "Type": "json",
        "SCHUL_NM": name
    })

    try:
        data = res.json().get("schoolInfo")

        if not data:
            return None

        rows = data[1].get("row", [])

        if not rows:
            return None

        row = rows[0]

        return {
            "name": row.get("SCHUL_NM"),
            "address": row.get("ORG_RDNMA"),
            "office": row.get("ATPT_OFCDC_SC_NM"),
            "type": row.get("SCHUL_KND_SC_NM")
        }

    except:
        return None


# -----------------------------
# 자동완성 API
# -----------------------------
@app.get("/auto")
def auto(q: str):

    url = "https://open.neis.go.kr/hub/schoolInfo"

    res = requests.get(url, params={
        "KEY": NEIS_KEY,
        "Type": "json",
        "SCHUL_NM": q
    })

    try:
        data = res.json().get("schoolInfo")

        if not data:
            return {"data": []}

        rows = data[1].get("row", [])

        return {
            "data": [r.get("SCHUL_NM") for r in rows[:5]]
        }

    except:
        return {"data": []}


# -----------------------------
# 검색 API
# -----------------------------
@app.get("/search")
def search(q: str):

    data = get_school(q)

    if not data:
        return {"data": []}

    return {"data": [data]}


# -----------------------------
# 기본 확인용
# -----------------------------
@app.get("/")
def home():
    return {"message": "School API Running"}
