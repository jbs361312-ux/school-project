from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import os
import random

# OpenAI (선택 기능)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USE_AI = True
except:
    USE_AI = False


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
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if "schoolInfo" not in data:
            return []

        return data["schoolInfo"][1]["row"]

    except:
        return []


# -----------------------------
# AI 이미지 생성
# -----------------------------
def generate_ai_image(name):

    if USE_AI:

        try:
            prompt = f"modern korean high school classroom, {name}, realistic, bright lighting"

            res = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )

            return res.data[0].url

        except:
            pass

    # fallback (무료 이미지)
    seed = random.randint(1, 9999)
    return f"https://source.unsplash.com/600x400/?school,classroom,{name}&sig={seed}"


# -----------------------------
# 웹페이지
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

body{
    font-family: Arial;
    background: linear-gradient(135deg,#74ebd5,#acb6e5);
    text-align:center;
}

/* 카드 애니메이션 */
.card{
    background:white;
    width:500px;
    margin:20px auto;
    padding:20px;
    border-radius:20px;
    box-shadow:0 10px 20px rgba(0,0,0,0.2);
    animation: fade 0.5s ease-in-out;
}

@keyframes fade{
    from{opacity:0; transform:translateY(20px);}
    to{opacity:1; transform:translateY(0);}
}

/* 이미지 슬라이드 */
.slide{
    width:100%;
    height:250px;
    border-radius:10px;
    transition:0.5s;
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
    cursor:pointer;
}

a{
    text-decoration:none;
    color:blue;
}

</style>

</head>

<body>

<h1>🤖 AI 학교 플랫폼</h1>

<input id="name" placeholder="학교 입력">
<button onclick="search()">검색</button>

<div id="result"></div>

<script>

let images = [];
let index = 0;

// 이미지 슬라이드
function startSlide(imgList){

    images = imgList;
    index = 0;

    setInterval(()=>{

        const img = document.getElementById("slideImg");
        if(img && images.length > 0){
            index = (index + 1) % images.length;
            img.src = images[index];
        }

    }, 2500);
}


// 검색
async function search(){

    const name = document.getElementById("name").value;

    const res = await fetch(`/api?name=${name}`);
    const data = await res.json();

    const box = document.getElementById("result");

    if(data.data.length === 0){
        box.innerHTML = "❌ 없음";
        return;
    }

    let html = "";

    data.data.forEach((s, i)=>{

        html += `
        <div class="card">

            <h2>${s.SCHUL_NM}</h2>

            <img id="slideImg" class="slide" src="${s.images[0]}">

            <p>📍 ${s.ORG_RDNMA}</p>

            <p>🏢 ${s.ATPT_OFCDC_SC_NM}</p>

            <p>🎓 ${s.SCHUL_KND_SC_NM}</p>

            <p>
            <a href="https://www.google.com/maps/search/${s.ORG_RDNMA}" target="_blank">
            🗺 지도 보기
            </a>
            </p>

        </div>
        `;

        startSlide(s.images);

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

        images = [
            generate_ai_image(s["SCHUL_NM"]),
            generate_ai_image(s["SCHUL_NM"] + " classroom"),
            generate_ai_image(s["SCHUL_NM"] + " students")
        ]

        result.append({
            **s,
            "images": images
        })

    return {"data": result}
