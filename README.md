# school-project
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

templates = Jinja2Templates(directory=".")

# 🔑 교육청 API 키 (여기에 입력)
NEIS_KEY = "여기에_교육청_API_키"

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
        res = requests.get(url, params=params)
        row = res.json()["schoolInfo"][1]["row"][0]

        return {
            "name": row["SCHUL_NM"],
            "address": row["ORG_RDNMA"],
            "office": row["ATPT_OFCDC_SC_NM"],
            "type": row["SCHUL_KND_SC_NM"]
        }

    except:
        return None


# -----------------------------
# 웹 페이지 (HTML 직접 포함)
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>학교 검색 시스템</title>

<style>
body {
    font-family: Arial;
    background: linear-gradient(135deg, #74ebd5, #acb6e5);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
}

.box {
    background: white;
    padding: 40px;
    border-radius: 20px;
    width: 500px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

input {
    padding: 10px;
    width: 70%;
    border-radius: 10px;
    border: 1px solid #ccc;
}

button {
    padding: 10px 15px;
    border: none;
    background: #4a90e2;
    color: white;
    border-radius: 10px;
    cursor: pointer;
}

button:hover {
    background: #357abd;
}

.card {
    margin-top: 20px;
    padding: 20px;
    background: #f7f7f7;
    border-radius: 15px;
}

.fail {
    color: red;
}
</style>

</head>

<body>

<div class="box">

<h1>🏫 학교 검색 시스템</h1>

<input id="name" placeholder="학교 이름 입력">
<button onclick="search()">검색</button>

<div id="result"></div>

</div>

<script>
async function search() {

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    const box = document.getElementById("result");

    if (data.result === "fail") {
        box.innerHTML = "<p class='fail'>검색 실패</p>";
        return;
    }

    box.innerHTML = `
        <div class="card">
            <h2>${data.data.name}</h2>
            <p>📍 ${data.data.address}</p>
            <p>🏢 ${data.data.office}</p>
            <p>🎓 ${data.data.type}</p>
        </div>
    `;
}
</script>

</body>
</html>
"""


# -----------------------------
# API (데이터 반환)
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
