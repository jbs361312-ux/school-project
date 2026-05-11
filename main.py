from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI()

NEIS_KEY = os.getenv("NEIS_KEY")


# -----------------------------
# 학교 검색 함수
# -----------------------------
def get_school(name):

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
# HTML 페이지
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>학교 검색</title>

<style>
body {
    font-family: sans-serif;
    background: #f5f6fa;
    text-align: center;
    padding: 40px;
}

.box {
    background: white;
    padding: 30px;
    border-radius: 15px;
    width: 400px;
    margin: auto;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

input {
    width: 80%;
    padding: 10px;
    margin-top: 10px;
}

button {
    padding: 10px 20px;
    margin-top: 10px;
    cursor: pointer;
}

.card {
    margin-top: 20px;
    padding: 15px;
    background: #eef;
    border-radius: 10px;
}
</style>
</head>

<body>

<div class="box">

<h2>🏫 학교 검색</h2>

<input id="name" placeholder="학교 이름 입력">
<br>
<button onclick="search()">검색</button>

<div id="result"></div>

</div>

<script>

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
            <h3>${s.name}</h3>
            <p>📍 ${s.address}</p>
            <p>🏢 ${s.office}</p>
            <p>🎓 ${s.type}</p>
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

    data = get_school(name)

    if not data:
        return {"result": False}

    return {
        "result": True,
        "data": data
    }
