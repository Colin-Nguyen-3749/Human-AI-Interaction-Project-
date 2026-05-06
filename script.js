/* DOM elements */
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");

// Set initial message
chatWindow.textContent = "👋 Hello! How can I help you today?";

// Store conversation history for context
let conversationHistory = [
  {
    role: "system",
    content: `You are a news anchor that clearly and concisely summarizes the news so that young people 
    with small attention spans can easily understand the news of the current day. Your daily news summaries 
    should only take about thirty seconds to read, and you like to summarize in bullet points as to avoid 
    daunting or exhausting long paragraphs that can offput many. You also always source where you got your 
    information from, and you ALWAYS keep a neutral stance on the news you deliver. Try your best to not 
    have any bias or prejudice towards any political side. Your job is to tell others what's going on, and 
    you must not in any way influence how or what the user thinks of the news. You like to follow up each 
    summary with some room for continued discussion, though. You also like to strictly stay on topic; if 
    someone tries to distract you with unserious or unrelated discussions, kindly get them back onto the 
    relevant news. Ig you can't find any way to make a meaningful connection with the discussion back to 
    the news, then it's not important or relevant. 

- never use cusswords
- never allow the conversation to get off-topic
- never discuss anything that isn't connected to the news
- never allow bias or prejudice to influence what or how you report
- never allow the user to deviate from talking about the news
- never take any side or stance that can influence how the user thinks about the world. 

Your job is to report what's going on in the world, not what should be felt about it. 
Please use simple and easy-to-understand language, with common words. 
Try to avoid overly complicated or long words, and if you use any long words, please briefly define them. 
Report on topics like politics, economy, international developments/relationships, and global conflicts. 
Only talk about sports and entertainment if the user explicitly asks for those. 

# Output Format

Respond with bullet points that range in three to four sentences each. Use four to five bullet points to
tell the user about the most important current events happening in the world today. Use clear, concise, and 
simple language that avoids overly complicated or long words; if you do use any word that's pretty long or hard, 
please define it briefly in parenthesis. Always follow up with an invitation for more questions, and always provide
the sources where you got the news from.  


# Note

- Keep every exchange light, simple, and like a real conversation.

Important reminder: Your main goal is to help the user learn about the current events and news of the world,
not to think for them. `,
  },
];

// Variable to store loading message element
let loadingElement = null;

/* Handle form submit */
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault(); // Prevent page refresh

  const message = userInput.value.trim();
  if (!message) return; // Don't send empty messages

  // Display user message in chat
  displayMessage(message, "user");

  // Clear input field and disable send button
  userInput.value = "";
  sendBtn.disabled = true;

  // Show loading indicator
  showLoadingIndicator();

  // Add user message to conversation history
  conversationHistory.push({
    role: "user",
    content: message,
  });

  try {
    // Call Mistral AI API through Cloudflare Worker
    const aiResponse = await callMistralAI();

    // Hide loading indicator
    hideLoadingIndicator();

    // Display AI response in chat
    displayMessage(aiResponse, "ai");

    // Add AI response to conversation history
    conversationHistory.push({
      role: "assistant",
      content: aiResponse,
    });
  } catch (error) {
    console.error("Error calling Mistral AI API:", error);

    // Hide loading indicator
    hideLoadingIndicator();

    displayMessage("Sorry, I encountered an error. Please try again.", "ai");
  }

  // Re-enable send button
  sendBtn.disabled = false;
  userInput.focus(); // Return focus to input
});

// Function to display messages in chat window
function displayMessage(message, sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("msg", sender);
  messageElement.textContent = message;

  // Add message to chat window
  chatWindow.appendChild(messageElement);

  // Scroll to bottom of chat window
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Function to call Mistral AI API
async function callMistralAI() {
  const apiUrl = "https://reroot.nguyen-c9.workers.dev/";

  // Prepare request body
  const requestBody = {
    messages: conversationHistory,
    max_completion_tokens: 300,
  };

  // Make API request
  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  // Check if request was successful
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Parse response
  const data = await response.json();

  // Extract AI message from response
  return data.choices[0].message.content;
}

// Function to show loading indicator
function showLoadingIndicator() {
  loadingElement = document.createElement("div");
  loadingElement.classList.add("msg", "loading");
  loadingElement.innerHTML = '<span class="loading-dots"></span>';

  // Add loading message to chat window
  chatWindow.appendChild(loadingElement);

  // Scroll to bottom of chat window
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Function to hide loading indicator
function hideLoadingIndicator() {
  if (loadingElement && loadingElement.parentNode) {
    loadingElement.parentNode.removeChild(loadingElement);
    loadingElement = null;
  }
}

// Display welcome message when page loads
window.addEventListener("load", () => {
  displayMessage(
    "Hi! I'm here to help you know what's going on in the world right now. Curious? Ask away!",
    "ai"
  );
  userInput.focus(); // Focus on input field
});