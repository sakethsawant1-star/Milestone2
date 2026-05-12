import os
import sys

# Add the root directory to path to import phase2
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from phase2_rag.rag_pipeline import RAGPipeline

class IntentClassifier:
    def __init__(self, groq_client):
        self.groq_client = groq_client
        self.model_name = 'llama-3.3-70b-versatile'

    def is_safe_query(self, query):
        """
        Analyzes the query intent.
        Returns False if it asks for investment advice, opinions, or is completely unrelated.
        Returns True if it's a factual mutual fund query.
        """
        prompt = f"""
        Analyze the following user query: "{query}"
        
        Does this query ask for investment advice, opinions, future predictions, or is it completely unrelated to mutual funds? 
        If it is asking for advice (e.g. "Should I buy", "Is this good") or is unrelated (e.g. "What is the weather"), reply with YES.
        If it is asking for objective, factual information about a mutual fund (e.g. "What is the NAV", "What is the exit load"), reply with NO.
        
        Reply with ONLY the word YES or NO.
        """
        
        response = self.groq_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        result = response.choices[0].message.content.strip().upper()
        # YES means it IS asking for advice/unrelated -> NOT safe
        # NO means it IS NOT asking for advice -> IS safe
        return "NO" in result

def safe_answer_query(query, pipeline, classifier):
    print(f"--- Processing Query: '{query}' ---")
    print("Checking Guardrails...")
    
    is_safe = classifier.is_safe_query(query)
    
    if not is_safe:
        print("Guardrail Check: FAILED (Flagged as Advisory/Out-of-box)")
        refusal_msg = "I can only provide factual information about mutual funds. I cannot offer investment advice or answer unrelated queries."
        print("\nFinal Answer:\n")
        print(refusal_msg)
        print("-" * 50 + "\n")
        return refusal_msg
        
    print("Guardrail Check: PASSED")
    # If safe, bypass the internal print statement of answer_query by just calling it
    # We will let answer_query do its own printing for now.
    return pipeline.answer_query(query)

if __name__ == "__main__":
    print("Initializing Pipeline and Guardrails...")
    rag_pipeline = RAGPipeline()
    classifier = IntentClassifier(rag_pipeline.groq_client)
    
    print("\n" + "="*50)
    # Test 1: Safe Factual Query
    safe_answer_query("What is the NAV of HDFC Small Cap?", rag_pipeline, classifier)
    
    # Test 2: Advisory Query
    safe_answer_query("Should I invest my life savings in HDFC Flexi Cap?", rag_pipeline, classifier)
    
    # Test 3: Unrelated Query
    safe_answer_query("What is the capital of France?", rag_pipeline, classifier)
