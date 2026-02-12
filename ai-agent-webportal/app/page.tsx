'use client';

import logo from './images/385d3b78-9b9a-472f-901f-7e0abb3c4c90_removalai_preview.png';
import Image from 'next/image'
import { useState } from "react";


export default function Home() {
  
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");

  const handleClarify = async () => {
    //1. check if input has text and add user input to conversation
    if(input) {
      setResponse((prev) => prev + `${input} \n`);
    } else {
      return;
    }

    //2. send input to backend to get response from agent and clear input box
    const res = await fetch("http://localhost:3001/api/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });
    setInput("");

    //3. append the agent response to the conversation
    const data = await res.json();
    console.log(data);
    setResponse((prev) => prev + "\n" + `THEIOS: ${data.response} \n\n`)
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
            <textarea placeholder="Have any questions?" value={response} onChange={(e) => setInput(e.target.value)} />
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder='Type questions here...' />
            <button onClick={handleClarify}>Clarify</button>
          </div>

        </main>
      </div>
    </div>
  );
}
