from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import urllib.parse

app = FastAPI()

NEIS_KEY = os.getenv("NEIS_KEY")
BASE_URL = "https://school-project-lowd.onrender.com"


# -----------------------------
# 학교 정보
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
        address = row.get("ORG_RDNMA")

        return {
            "name": row.get("SCHUL_NM"),
            "address": address,
            "office": row.get("ATPT_OFCDC_SC_NM"),
            "type": row.get("SCHUL_KND_SC_NM"),

            # 🗺 지도
            "map": f"https://www.google.com/maps/search/{urllib.parse.quote(address)}",

            # 📱 QR (홈페이지 접속)
            "qr": f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={BASE_URL}"
        }

    except:
        return None


# -----------------------------
# 자동완성
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
# API
# -----------------------------
@app.get("/api")
def api(name: str):

    data = get_school(name)

    if not data:
        return {"result": False}

    return {"result": True, "data": data}


# -----------------------------
# HTML (이미지 UI 버전)
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI 학교 플랫폼</title>

<style>

/* 🌄 네가 준 공부 이미지 배경 */
body {
    margin: 0;
    font-family: sans-serif;

    background: url('https://images.unsplash.com/photo-1503676260728-1c00da094a0b') center/cover fixed;
}

/* 🧊 메인 카드 */
.box {
    width: 500px;
    margin: 60px auto;
    padding: 25px;

    background: rgba(255,255,255,0.92);
    border-radius: 18px;

    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    text-align: center;
}

input {
    width: 80%;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #ccc;
}

button {
    padding: 10px 20px;
    margin-top: 10px;
    border: none;
    background: #4a90e2;
    color: white;
    border-radius: 10px;
    cursor: pointer;
}

button:hover {
    background: #357bd8;
}

/* 📦 결과 카드 */
.card {
    margin-top: 20px;
    padding: 15px;
    background: white;
    border-radius: 12px;
    text-align: left;
}

.auto {
    cursor: pointer;
    color: #1a73e8;
}
</style>
</head>

<body>

<div class="box">

<h2>🏫 AI 학교 검색</h2>

<input id="name" oninput="auto()" placeholder="학교 이름 입력">
<br>
<button onclick="search()">검색</button>

<div id="autoBox"></div>
<div id="result"></div>

</div>

<script>

// 🔎 자동완성
async function auto() {

    const q = document.getElementById("name").value;

    if (q.length < 2) return;

    const res = await fetch(`/auto?q=${q}`);
    const data = await res.json();

    document.getElementById("autoBox").innerHTML =
        data.data.map(n => `
            <p class="auto" onclick="select('${n}')">🔎 ${n}</p>
        `).join("");
}

function select(name) {
    document.getElementById("name").value = name;
}


// 🔍 검색
async function search() {

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    const box = document.getElementById("result");

    if (!data.result) {
        box.innerHTML = "<p>검색 실패</p>";
        return;
    }

    const s = data.data;

    box.innerHTML = `
        <div class="card">

            <h2>🏫 ${s.name}</h2>

            <p>📍 ${s.address}</p>
            <p>🏢 ${s.office}</p>
            <p>🎓 ${s.type}</p>

            <a href="${s.map}" target="_blank">🗺 지도 보기</a>

            <br><br>

            <img src="${s.qr}" style="width:150px">

        </div>
    `;
}

</script>

</body>
</html>
"""
