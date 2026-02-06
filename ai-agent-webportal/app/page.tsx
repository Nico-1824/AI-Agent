'use client';

import logo from './images/385d3b78-9b9a-472f-901f-7e0abb3c4c90_removalai_preview.png';
import Image from 'next/image'
import { useState } from "react";


export default function Home() {
  
  const [response, setResponse] = useState("");
  const [input, setInput] = useState("");

  const handleClarify = async () => {
    const res = await fetch("/api/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });

    const data = await res.json();
    setInput((prev) => prev + "\n\n" + `Theios: ${data.response}`)
  };

  return (
    <div className="app-container">
      <header>
        <div className='title'>
          <h1>THEIOS</h1>
          <h2>YOUR PERSONAL AI AGENT</h2>
        </div>
        <Image className="image" src={logo} alt="LOGO" width={140} height={100} />
      </header>
      <div>
        <main>

          <div className="conversation-container">

          </div>

          <div className="prompt-container">
            <textarea placeholder="Have any questions?" value={input} onChange={(e) => setInput(e.target.value)} />
            <button onClick={handleClarify}>Clarify</button>
          </div>

        </main>
      </div>
    </div>
  );
}
