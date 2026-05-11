from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import qrcode
import base64
from io import BytesIO

app = FastAPI()

NEIS_KEY = os.getenv("NEIS_KEY")

# -----------------------------
# 학교 데이터 (전국 검색)
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
        row = r.json()["schoolInfo"][1]["row"][0]

        return {
            "name": row["SCHUL_NM"],
            "address": row["ORG_RDNMA"],
            "office": row["ATPT_OFCDC_SC_NM"],
            "type": row["SCHUL_KND_SC_NM"]
        }

    except:
        return None


# -----------------------------
# QR 코드 생성
# -----------------------------
def make_qr(url):
    img = qrcode.make(url)

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()


# -----------------------------
# 웹 UI
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>학교 AI 시스템</title>

<style>
body{
    font-family: Arial;
    background: linear-gradient(135deg,#74ebd5,#acb6e5);
    text-align:center;
}

.card{
    background:white;
    padding:20px;
    margin:20px auto;
    width:400px;
    border-radius:15px;
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
    width:300px;
    border-radius:10px;
}
</style>

</head>

<body>

<h1>🏫 AI 학교 검색 시스템</h1>

<input id="name" placeholder="학교 입력">
<button onclick="search()">검색</button>

<div id="result"></div>

<script>
async function search(){

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    if(data.result == "fail"){
        document.getElementById("result").innerHTML = "검색 실패";
        return;
    }

    document.getElementById("result").innerHTML = `
        <div class="card">
            <h2>${data.school.name}</h2>
            <p>${data.school.address}</p>
            <p>${data.school.office}</p>
            <p>${data.school.type}</p>

            <h3>📱 QR 접속</h3>
            <img src="data:image/png;base64,${data.qr}">
        </div>
    `;
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

    school = get_school(name)

    if not school:
        return {"result": "fail"}

    # 현재 URL (Render 자동 대응)
    url = "https://your-site.onrender.com/?school=" + name

    qr = make_qr(url)

    return {
        "result": "success",
        "school": school,
        "qr": qr
    }
