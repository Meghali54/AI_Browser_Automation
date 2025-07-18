import React, { useState } from 'react';
import './App.css';


function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  // Use a random user_id for demo session continuity
  const [userId] = useState(() => 'user_' + Math.random().toString(36).slice(2, 10));
  const [expect, setExpect] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    setMessages(msgs => [...msgs, { sender: 'user', text: input }]);
    setLoading(true);
    const res = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: input, user_id: userId })
    });
    const data = await res.json();
    setLoading(false);

    // If backend returns step-by-step flow
    if (data.steps && Array.isArray(data.steps)) {
      // Show each step and screenshot in order
      let newMsgs = [];
      for (let i = 0; i < data.steps.length; ++i) {
        newMsgs.push({ sender: 'agent', text: data.steps[i] });
        if (data.screenshots && data.screenshots[i]) {
          newMsgs.push({ sender: 'agent', screenshot: '/api' + data.screenshots[i] });
        }
      }
      setMessages(msgs => [...msgs, ...newMsgs]);
      setExpect(null);
      setInput('');
      return;
    }

    // Otherwise, show status and set next expected input
    setMessages(msgs => [...msgs, { sender: 'agent', text: data.status }]);
    setExpect(data.expect || null);
    setInput('');
  };

  // Show dynamic placeholder based on what the agent expects
  let placeholder = 'Type a command...';
  if (expect === 'email') placeholder = 'Enter your Gmail address...';
  if (expect === 'password') placeholder = 'Enter your Gmail password...';
  if (expect === 'leave_dates') placeholder = 'When will you be taking leave?';
  if (expect === 'manager_email') placeholder = "Enter your manager's email...";

  return (
    <div className="App">
      <h2>AI Browser Agent</h2>
      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={msg.sender}>
            {msg.text && <div className="msg-text">{msg.text}</div>}
            {msg.screenshot && <img src={msg.screenshot} alt="screenshot" className="screenshot" />}
          </div>
        ))}
        {loading && <div className="agent"><div className="msg-text">Agent is typing...</div></div>}
      </div>
      <div className="input-row">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder={placeholder}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  );
}

export default App;
