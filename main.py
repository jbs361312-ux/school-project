from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import urllib.parse
import random

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

            "map": f"https://www.google.com/maps/search/{urllib.parse.quote(address)}",

            # 📱 QR 코드 (학교 페이지 or 앱 접속)
            "qr": f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={BASE_URL}/?school={urllib.parse.quote(name)}"
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

        return {"data": [r.get("SCHUL_NM") for r in rows[:5]]}

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
# HTML
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI School App</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body {
    margin:0;
    font-family:sans-serif;
    background:#f5f5f5;
}

/* DARK MODE */
.dark {
    background:#111;
    color:white;
}

.box {
    width:90%;
    max-width:500px;
    margin:20px auto;
    padding:15px;
    background:white;
    border-radius:15px;
}

.dark .box {
    background:#1e1e1e;
}

input {
    width:80%;
    padding:10px;
    border-radius:10px;
}

button {
    padding:10px;
    margin:5px;
    border:none;
    border-radius:10px;
    cursor:pointer;
}

.auto {
    cursor:pointer;
    color:#1a73e8;
}

.nav {
    position:fixed;
    bottom:0;
    left:0;
    width:100%;
    display:flex;
    justify-content:space-around;
    background:#222;
    color:white;
    padding:10px 0;
}

.page { display:none; }
.active { display:block; }

</style>
</head>

<body>

<!-- 🔊 MUSIC -->
<audio id="bgm" loop>
<source src="https://cdn.pixabay.com/download/audio/2022/10/25/audio_3b7c2c3b6c.mp3">
</audio>

<!-- PAGE -->
<div id="home" class="page active">
<div class="box">

<h2>🏫 AI 학교 검색</h2>

<input id="name" oninput="auto()" placeholder="학교 입력">

<br>

<button onclick="search()">검색</button>
<button onclick="addSchool()">➕ 추가</button>
<button onclick="aiRecommend()">🤖 추천</button>
<button onclick="toggleDark()">다크</button>
<button onclick="toggleMusic()">음악</button>

<div id="autoBox"></div>
<div id="result"></div>

<h4>📌 선택 리스트</h4>
<div id="list"></div>

</div>
</div>

<!-- GRAPH -->
<div id="compare" class="page">
<div class="box">
<h2>📊 비교</h2>
<canvas id="chart"></canvas>
</div>
</div>

<!-- NAV -->
<div class="nav">
<button onclick="show('home')">홈</button>
<button onclick="show('compare')">비교</button>
</div>

<script>

// ---------------- NAV ----------------
function show(id){
    document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// ---------------- MUSIC ----------------
let music = document.getElementById("bgm");
let play = false;

function toggleMusic(){
    if(play) music.pause();
    else music.play();
    play = !play;
}

// ---------------- DARK ----------------
function toggleDark(){
    document.body.classList.toggle("dark");
}

// ---------------- AUTO ----------------
async function auto(){

    const q = document.getElementById("name").value;
    if(q.length < 2) return;

    const res = await fetch(`/auto?q=${q}`);
    const data = await res.json();

    document.getElementById("autoBox").innerHTML =
        data.data.map(n =>
            `<p class="auto" onclick="select('${n}')">🔎 ${n}</p>`
        ).join("");
}

function select(n){
    document.getElementById("name").value = n;
}

// ---------------- SEARCH ----------------
async function search(){

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    if(!data.result){
        document.getElementById("result").innerHTML = "❌ 실패";
        return;
    }

    const s = data.data;

    document.getElementById("result").innerHTML = `
        <div style="background:white;padding:10px;border-radius:10px">

            <h3>${s.name}</h3>
            <p>${s.address}</p>

            <a href="${s.map}" target="_blank">🗺 지도</a>

            <br><br>

            <!-- 📱 QR 코드 -->
            <img src="${s.qr}" width="150">

        </div>
    `;
}

// ---------------- LIST ----------------
let schoolList = [];

function addSchool(){

    const name = document.getElementById("name").value;

    if(name && !schoolList.includes(name)){
        schoolList.push(name);
    }

    renderList();
}

function renderList(){

    document.getElementById("list").innerHTML =
        schoolList.map(s => `<p>📌 ${s}</p>`).join("");
}

// ---------------- AI 추천 ----------------
function aiRecommend(){

    if(schoolList.length === 0){
        alert("학교 추가 먼저!");
        return;
    }

    const pick = schoolList[Math.floor(Math.random()*schoolList.length)];

    document.getElementById("result").innerHTML =
        "🤖 추천: <b>" + pick + "</b>";
}

// ---------------- CHART ----------------
new Chart(document.getElementById("chart"), {
    type:"bar",
    data:{
        labels:["전주고","상산고","과학고","풍남중"],
        datasets:[{
            label:"점수",
            data:[70,95,90,60]
        }]
    }
});

</script>

</body>
</html>
"""
