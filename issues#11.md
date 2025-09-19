### Task 11.1.1 – Create a chatbot AI page
 
**What it does:** Create a chatbot UI that allows users to type any question. The chatbot should generate answers based on the entire previous conversation (historical context). Display each answer immediately above its corresponding question, maintaining chronological order. Differentiate clearly between questions and answers in the UI
 
**Prompt:**
 
> Create new pages `ChatAsk.jsx` in pages folder frontend to implement a chatbot UI. Add a text input field and submit button to allow users to type and send questions. Store the conversation history in a reactive array of message objects { role: "user" | "bot", content: string }.
 
When the user submits a question, append it to the conversation history. Then call generateReply(messages) from src/lib/api.js, passing the full message history including the new question. Append the bot's reply to the history once received.
 
In the UI, render the messages in chronological order (top to bottom). For each user message, display the corresponding bot reply immediately below it. Use visual styling (e.g., colors or alignment) to clearly differentiate between user questions and bot answers.
 
Ensure the input is cleared after submission and auto-scrolls to the latest message.
 
**Objective**
Implement a conversational interface that preserves context and shows answers above questions.
 
**Acceptance Criteria:**
 
* [ ] User can input questions and get answers.
* [ ] Answers reflect previous conversation context.
* [ ] Each answer is displayed immediately above its question
* [ ] Chat history is scrollable and visually clear.