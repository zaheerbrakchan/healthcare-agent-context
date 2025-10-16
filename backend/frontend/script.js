let activeAgent = null;
let chatHistory = []; // store session chat

function openChat(agent) {
  activeAgent = agent;

  // Highlight active agent card
  document.querySelectorAll(".agent-card").forEach(card => card.classList.remove("active-card"));
  const cardToHighlight = agent === "appointment" ? document.querySelector(".agent-card:nth-child(1)")
                                                  : document.querySelector(".agent-card:nth-child(2)");
  cardToHighlight.classList.add("active-card");

  document.getElementById("chatPopup").classList.remove("hidden");
  document.getElementById("chatTitle").innerText =
    agent === "appointment" ? "🩺 Appointment Agent" : "📋 Preassessment Agent";
  document.getElementById("chatMessages").innerHTML = "";
  chatHistory = [];

  // Add default welcome message
  const welcomeMsg = agent === "appointment"
      ? "Hi! Welcome to ABC Hospital. I am your appointment assistant. How can I help you today?"
      : "Hello! Welcome to ABC Hospital. I am your preassessment assistant. Let's start by taking a few details.";
  appendMessage("bot", welcomeMsg);
}

function closeChat() {
  document.getElementById("chatPopup").classList.add("hidden");
  activeAgent = null;
  chatHistory = [];

  // Remove card highlight
  document.querySelectorAll(".agent-card").forEach(card => card.classList.remove("active-card"));
}

function appendMessage(role, text) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", role);
  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;
  msgDiv.appendChild(bubble);
  document.getElementById("chatMessages").appendChild(msgDiv);
  const messagesDiv = document.getElementById("chatMessages");
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("chatQuery");
  const query = input.value.trim();
  if (!query || !activeAgent) return;

  appendMessage("user", query);
  input.value = "";

  const url =
    activeAgent === "appointment"
      ? `/appointment/chat`
      : `/preassessment/chat`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: query }),
    });
    const data = await res.json();

    // Unwrap JSON reply if needed
    let reply;
    if (typeof data === "object") {
      reply = data.reply || JSON.stringify(data, null, 2);
    } else {
      reply = data;
    }

    appendMessage("bot", reply);
  } catch (err) {
    appendMessage("bot", "⚠️ Error: " + err.message);
  }
}
