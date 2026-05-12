# Edge Cases & Mitigation Strategy

This document outlines the potential edge cases for each phase of the Mutual Fund FAQ Assistant architecture and proposes mitigation strategies to ensure system robustness and compliance.

## Phase 0: Project Context & Reference URLs
* **Edge Case:** **Groww URL structure changes or returns 404.**
  * *Mitigation:* Implement a URL validation check before ingestion. If a URL fails, alert the admin to update the Phase 0 configuration with the new URL.
* **Edge Case:** **Groww implements strict anti-scraping measures (CAPTCHA / Cloudflare).**
  * *Mitigation:* Since this is a one-time/infrequent ingestion of only 6 URLs, use a headed browser (like Playwright/Selenium) or manual HTML saving if automated HTTP requests are blocked.
* **Edge Case:** **Fund names or categories change (e.g., scheme mergers).**
  * *Mitigation:* Periodically verify the scheme names against the URLs. Maintain a static mapping of the 6 approved funds.

## Phase 1: Data Ingestion & Knowledge Base Preparation
* **Edge Case:** **Dynamic content loading (JavaScript required).**
  * *Mitigation:* Use tools that render JavaScript (e.g., Playwright or Puppeteer) rather than simple `requests` or `BeautifulSoup` to ensure all data points (like expense ratios) are captured.
* **Edge Case:** **"Last updated" date is missing or inconsistently formatted on the page.**
  * *Mitigation:* Fallback to the ingestion timestamp (e.g., "Data retrieved on [Date]") if an explicit page update date cannot be parsed reliably.
* **Edge Case:** **Inconsistent HTML structure across the 6 scheme pages.**
  * *Mitigation:* Rely on visible text extraction and robust chunking rather than strict HTML element targeting (XPath/CSS selectors) which might break.

## Phase 2: RAG Pipeline Development (Retrieval & Generation)
* **Edge Case:** **Query asks for factual info NOT present in the 6 Groww pages.**
  * *Mitigation:* Enforce a strict "I don't know" fallback in the LLM prompt. The LLM must not hallucinate or use its internal knowledge base. Example response: "The requested information is not available in the provided documents."
* **Edge Case:** **Conflicting information within the same page or chunks.**
  * *Mitigation:* Instruct the LLM to state the most explicitly defined fact or mention both if unclear, without analyzing which is "better".
* **Edge Case:** **Prompt Injection / Jailbreaking to bypass constraints.**
  * *Mitigation:* Use strong system prompts isolating the constraints from the user query. The instruction to output only 3 sentences and 1 citation must be enforced post-generation via a validation check if necessary.

## Phase 3: Compliance & Refusal Guardrails
* **Edge Case:** **Borderline queries (e.g., "Is an exit load of 1% high for this fund?").**
  * *Mitigation:* Train the intent classifier to err on the side of caution. Any subjective adjectives ("high", "good", "better") should trigger the refusal handler.
* **Edge Case:** **Factual comparison queries (e.g., "What is the difference in expense ratio between the Mid-Cap and Small-Cap funds?").**
  * *Mitigation:* If the query strictly asks for facts, the RAG pipeline should retrieve both chunks and present the facts side-by-side without declaring a "winner". If the LLM struggles, the guardrail can route multi-fund queries to the refusal handler to be safe.
* **Edge Case:** **User includes PII in a factual query (e.g., "My PAN is ABCDE1234F, what is the ELSS lock-in?").**
  * *Mitigation:* Implement a regex-based PII scrubber before the query hits the intent classifier or the LLM.

## Phase 4: User Interface & Deployment
* **Edge Case:** **LLM API latency or timeouts.**
  * *Mitigation:* Implement a graceful loading state in the UI. If the API times out (e.g., >10 seconds), display a standard fallback error: "The service is temporarily unavailable. Please try again."
* **Edge Case:** **Malformed markdown in the LLM response breaking the UI (e.g., broken citation links).**
  * *Mitigation:* Implement a regex-based cleanup step on the backend before sending the response to the frontend to ensure the link and footer format `"Last updated from sources: <date>"` are strictly structured.
