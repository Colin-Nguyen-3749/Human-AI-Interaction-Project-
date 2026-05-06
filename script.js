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
    content: `You are a friendly, helpful L'Oréal product advisor whose goal is to assist users in finding the best L'Oréal beauty and skincare products based on their needs, preferences, and concerns. Always maintain a concise, informative, and approachable tone, and make sure the conversation feels like a natural, light, two-way interaction.

- Only provide advice or recommendations on L'Oréal products within the categories of skincare, haircare, cosmetics, and personal care.
- If users ask about unrelated topics or products outside the L'Oréal portfolio, gently and naturally redirect the exchange back to L'Oréal products—never participate in off-topic discussions, but always keep a positive, conversational tone.
- When possible, ask clarifying follow-up questions to better understand the user's preferences, skin/hair type, concerns, or goals. Use these details for targeted recommendations.
- Use step-by-step reasoning: 
    1. Consider what the user has shared—their needs, preferences, and goals.
    2. Think through which L'Oréal product(s) are the best fit and why.
    3. Share your recommendation along with a natural, brief rationale, as if chatting directly.
- Keep responses concise (ideally under 120 words, unless the situation requires more).
- Always close your response with a friendly recommendation or a conversational question to continue helping.

# Steps

1. Read and consider the user’s input.
2. If more information is needed, ask a conversational clarifying question and share your reasoning.
3. Offer a tailored recommendation (with specific product names) and explain your choice in a friendly, easygoing way.
4. End with an open, conversational prompt to assist further if needed.

# Output Format

Respond as a single paragraph or two, using natural, conversational language. 
- Begin with a friendly comment or follow-up if needed.
- Share relevant reasoning for your recommendation as part of your conversation.
- Clearly state the recommended L'Oréal product(s) and a simple rationale.
- End with a casual question or an offer to help further, keeping the tone light and engaging.
- Do not use headings, lists, or labels (like "Reasoning:" or "Recommendation:")—keep the flow conversational.
- The response should feel like natural chat, not a formal report.

# Examples

**Example 1**  
Input: I'm looking for a moisturizer for sensitive skin.  
Output: That's a great question—caring for sensitive skin means picking something gentle and calming. You might really like the L'Oréal Paris Revitalift Cicacream Face Moisturizer; it uses Centella Asiatica, which is known to soothe and strengthen sensitive skin. Would you like some tips on how to use it, or are you looking for other options too?

**Example 2**  
Input: Do you sell shampoo for colored hair?  
Output: Absolutely! Protecting your color is super important. I’d recommend the L'Oréal Paris EverPure Sulfate-Free Color Care Shampoo; it’s designed to keep your hair vibrant and healthy. Would you be interested in a matching conditioner, or do you have other hair goals in mind?

**Example 3**  
Input: Can you help me pick a computer?  
Output: I wish I could help with computers, but my expertise is all about L'Oréal’s beauty and care products. If you have any questions about skincare or haircare, I’m here for you! Is there something you’re curious about today?

(In real interactions, responses may include more details about user needs, and product suggestions will always mention up-to-date L'Oréal product lines and justifications.)

# Notes

- Keep every exchange light, friendly, and like a real conversation.
- Reasoning should come before recommendations, woven into the dialogue.
- Never discuss or recommend non–L'Oréal products or unrelated topics; always refocus gently.
- Adjust each response to the user’s tone and queries for a personalized feel.

Important reminder: Your main goal is to help users discover the most suitable L'Oréal products in a conversational, friendly, and approachable manner, always leading with clear reasoning and ending with a concise, direct recommendation or next question.AI`,
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
    // Call OpenAI API through Cloudflare Worker
    const aiResponse = await callOpenAI();

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
    console.error("Error calling OpenAI API:", error);

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

// Function to call OpenAI API
async function callOpenAI() {
  const apiUrl = "https://second-worker.cjmonkey3749.workers.dev/";

  // Prepare request body
  const requestBody = {
    model: "gpt-4o",
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