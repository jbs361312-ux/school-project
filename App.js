import { useState } from "react";

export default function App() {
 
  const [q, setQ] = useState("");
  const [auto, setAuto] = useState([]);
  const [list, setList] = useState([]);

  // 🔎 자동완성
  async function typing(e) {

    const value = e.target.value;
    setQ(value);

    if (value.length < 2) return;

    const res = await fetch(
      `https://school-api-lowd.onrender.com/auto?q=${value}`
    );

    const data = await res.json();
    setAuto(data.data);
  }


  // 🔍 검색
  async function search() {

    const res = await fetch(
      `https://school-api-lowd.onrender.com/search?q=${q}`
    );

    const data = await res.json();
    setList(data.data);
  }


  return (
    <div style={{
      padding: 20,
      fontFamily: "sans-serif",
      background: "#f5f6fa",
      minHeight: "100vh"
    }}>

      <h1>📱 AI 학교 플랫폼</h1>

      {/* 입력창 */}
      <input
        value={q}
        onChange={typing}
        placeholder="학교 입력"
        style={{ padding: 10, width: "70%" }}
      />

      <button onClick={search}>검색</button>

      {/* 🔎 자동완성 */}
      {auto.map((a, i) => (
        <p
          key={i}
          onClick={() => setQ(a)}
          style={{ cursor: "pointer", color: "blue" }}
        >
          🔎 {a}
        </p>
      ))}


      {/* 결과 */}
      {list.map((s, i) => (
        <div
          key={i}
          style={{
            margin: 15,
            padding: 15,
            borderRadius: 15,
            background: "white",
            boxShadow: "0 5px 15px rgba(0,0,0,0.1)"
          }}
        >

          <h2>🏫 {s.name}</h2>

          {/* 🖼 이미지 */}
          <img
            src={s.img}
            alt="school"
            style={{ width: "100%", borderRadius: 10 }}
          />

          <p>📍 {s.address}</p>
          <p>🏢 {s.office}</p>
          <p>🎓 {s.type}</p>

          {/* 🗺 지도 */}
          <a
            href={`https://www.google.com/maps/search/${s.address}`}
            target="_blank"
            rel="noreferrer"
          >
            🗺 지도 보기
          </a>

          {/* 📱 QR */}
          <div>
            <img
              src={`data:image/png;base64,${s.qr}`}
              alt="qr"
              style={{ width: 120, marginTop: 10 }}
            />
          </div>

        </div>
      ))}

    </div>
  );
}
