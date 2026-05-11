from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import os

app = FastAPI()

# HTML 템플릿 (파일 없이도 동작하게 inline 방식 유지)
templates = Jinja2Templates(directory=".")

# 🔑 교육청 API 키 (Render 환경변수 사용 권장)
NEIS_KEY = os.getenv("NEIS_KEY")

# -----------------------------
# 학교 정보 가져오기
# -----------------------------
def get_school(name):

    url = "https://open.neis.go.kr/hub/schoolInfo"

    params = {
        "KEY": NEIS_KEY,
        "Type": "json",
        "SCHUL_NM": name
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        row = data["schoolInfo"][1]["row"][0]

        return {
            "name": row.get("SCHUL_NM"),
            "address": row.get("ORG_RDNMA"),
            "office": row.get("ATPT_OFCDC_SC_NM"),
            "type": row.get("SCHUL_KND_SC_NM")
        }

    except:
        return None


# -----------------------------
# 웹페이지
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>학교 검색 API</title>

<style>
body{
    font-family: Arial;
    text-align:center;
    background:#f0f0f0;
    margin-top:100px;
}

.box{
    background:white;
    padding:30px;
    width:400px;
    margin:auto;
    border-radius:15px;
    box-shadow:0 5px 20px rgba(0,0,0,0.2);
}

input{
    padding:10px;
    width:70%;
}

button{
    padding:10px;
    background:#4a90e2;
    color:white;
    border:none;
    cursor:pointer;
}
</style>

</head>

<body>

<div class="box">

<h2>🏫 학교 검색</h2>

<input id="name" placeholder="학교 이름">
<button onclick="search()">검색</button>

<div id="result"></div>

</div>

<script>
async function search(){

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    const box = document.getElementById("result");

    if(data.result == "fail"){
        box.innerHTML = "검색 실패";
        return;
    }

    box.innerHTML = `
        <h3>${data.data.name}</h3>
        <p>${data.data.address}</p>
        <p>${data.data.office}</p>
        <p>${data.data.type}</p>
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

    data = get_school(name)

    if not data:
        return {"result": "fail"}

    return {
        "result": "success",
        "data": data
    }
