# Issues No 8

### Task 8.1.1 – Implement Chat Completion Backend with Vector Search

**Prompt:**

> Implement a backend feature to enable chat completion using the all FAISS vector store and all PDF metadata, leveraging Azure OpenAI's chat model. Update necessary variable on `.env` Include support for a default system prompt, which can be updated for future use cases.

**Acceptance Criteria:**

* [ ] Load context from FAISS and PDF metadata for user queries.
* [ ] Integrate Azure OpenAI chat model for generating responses.
* [ ] Use a default system prompt (configurable for future use cases).
* [ ] Provide an endpoint to update the default prompt.
* [ ] Ensure conversation context is preserved.
* [ ] Add tests for chat completion pipeline and prompt update.

**Notes:**

Store and load the default prompt from a config file or environment variable.
Document the chat completion API and prompt update mechanism.
Ensure compatibility with existing PDF/embedding features.