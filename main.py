from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import qrcode
from io import BytesIO
import base64

app = FastAPI()

NEIS_KEY = os.getenv("NEIS_KEY")

# -----------------------------
# 학교 검색
# -----------------------------
def get_school(name):

    url = "https://open.neis.go.kr/hub/schoolInfo"

    params = {
        "KEY": NEIS_KEY,
        "Type": "json",
        "SCHUL_NM": name
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        if "schoolInfo" not in data:
            return []

        return data["schoolInfo"][1]["row"]

    except:
        return []


# -----------------------------
# QR 생성
# -----------------------------
def make_qr(text):

    img = qrcode.make(text)

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()


# -----------------------------
# AI 이미지 (가짜 버전 - 안정용)
# -----------------------------
def ai_school_image(name):

    # 실제 AI 대신 안정 이미지 (Render용)
    return f"https://source.unsplash.com/600x400/?school,classroom,{name}"


# -----------------------------
# 메인 페이지
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>학교 AI 플랫폼</title>

<style>
body{
    font-family: Arial;
    background: linear-gradient(135deg,#74ebd5,#acb6e5);
    text-align:center;
}

.card{
    background:white;
    margin:20px auto;
    width:500px;
    padding:20px;
    border-radius:20px;
    box-shadow:0 10px 20px rgba(0,0,0,0.2);
}

input{
    padding:10px;
    width:60%;
}

button{
    padding:10px;
    background:#4a90e2;
    color:white;
    border:none;
}

img{
    width:100%;
    border-radius:10px;
}
</style>

</head>

<body>

<h1>🏫 AI 학교 플랫폼</h1>

<input id="name" oninput="auto()" placeholder="학교 입력">
<button onclick="search()">검색</button>

<div id="suggest"></div>
<div id="result"></div>

<script>

let timer;

// ---------------- 자동완성 ----------------
function auto(){

    clearTimeout(timer);

    timer = setTimeout(async ()=>{

        const name = document.getElementById("name").value;

        if(name.length < 2) return;

        const res = await fetch(`/api?name=${name}`);
        const data = await res.json();

        let box = document.getElementById("suggest");

        if(data.data.length > 0){
            box.innerHTML = "🔎 " + data.data[0].SCHUL_NM;
        }

    }, 300);
}


// ---------------- 검색 ----------------
async function search(){

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    let box = document.getElementById("result");

    if(data.data.length == 0){
        box.innerHTML = "❌ 없음";
        return;
    }

    let html = "";

    data.data.forEach(s => {

        html += `
        <div class="card">
            <h2>${s.SCHUL_NM}</h2>

            <img src="${s.img}">

            <p>📍 ${s.ORG_RDNMA}</p>

            <p>
            <a href="https://www.google.com/maps/search/${s.ORG_RDNMA}" target="_blank">
            🗺 지도 보기
            </a>
            </p>

            <img src="data:image/png;base64,${s.qr}">
        </div>
        `;
    });

    box.innerHTML = html;
}
</script>

</body>
</html>
"""


# -----------------------------
# API
# -----------------------------
@app.get("/api")
def api(name: str):

    schools = get_school(name)

    result = []

    for s in schools:

        url = "https://school.com/" + s["SCHUL_NM"]

        qr = make_qr(url)
        img = ai_school_image(s["SCHUL_NM"])

        result.append({
            **s,
            "qr": qr,
            "img": img
        })

    return {
        "data": result
    }
