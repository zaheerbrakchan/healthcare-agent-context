async function sendMessage() {
  const query = document.getElementById("query").value;
  const agent = document.getElementById("agent").value;
  const user_id = "user123"; // static for demo

  const res = await fetch(`http://localhost:8000/${agent}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, query })
  });

  const data = await res.json();
  document.getElementById("chat-box").innerHTML += `<p><b>You:</b> ${query}</p><p><b>${agent}:</b> ${data.response}</p>`;
  document.getElementById("query").value = "";
}
