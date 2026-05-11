from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import urllib.parse

app = FastAPI()

NEIS_KEY = os.getenv("NEIS_KEY")


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

            # 🖼 이미지
            "img": f"https://source.unsplash.com/600x400/?school,{name}",

            # 🗺 지도
            "map": f"https://www.google.com/maps/search/{urllib.parse.quote(address)}",

            # 📱 QR
            "qr": f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={urllib.parse.quote(address)}"
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
@app.get("/api")
def api(name: str):

    data = get_school(name)

    if not data:
        return {"result": False}

    return {"result": True, "data": data}


# -----------------------------
# HTML
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
body {
    font-family: sans-serif;
    background: #f5f6fa;
    text-align: center;
    padding: 30px;
}

.box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    width: 450px;
    margin: auto;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

input {
    width: 80%;
    padding: 10px;
}

button {
    padding: 10px 20px;
    margin-top: 10px;
}

.card {
    margin-top: 20px;
    padding: 15px;
    background: #eef;
    border-radius: 10px;
}

img {
    width: 100%;
    border-radius: 10px;
}

.auto {
    cursor: pointer;
    color: blue;
}
</style>
</head>

<body>

<div class="box">

<h2>🏫 AI 학교 검색</h2>

<input id="name" oninput="auto()" placeholder="학교 입력">
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

    const box = document.getElementById("autoBox");

    box.innerHTML = data.data.map(n => `
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

            <img src="${s.img}">

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
