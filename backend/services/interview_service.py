import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

QUESTION_BANK = {
    "SDE": [
        "Explain the difference between a stack and a queue. When would you use each?",
        "What is time complexity and why does it matter? Give an example.",
        "Explain what REST APIs are and how HTTP methods are used.",
        "What is the difference between SQL and NoSQL databases?",
        "Describe how you would debug a production issue.",
        "What is Git and explain the difference between merge and rebase.",
        "Explain object-oriented programming principles with examples.",
        "What is a memory leak and how would you identify one?",
    ],
    "AI Engineer": [
        "Explain the difference between supervised, unsupervised, and reinforcement learning.",
        "What is overfitting and how do you prevent it?",
        "Describe how transformers work in NLP.",
        "What is the difference between precision and recall?",
        "Explain gradient descent and its variants.",
        "What is RAG (Retrieval Augmented Generation) and when would you use it?",
        "How do you evaluate the performance of a language model?",
        "What is fine-tuning vs prompt engineering?",
    ],
    "Data Analyst": [
        "Explain the difference between mean, median, and mode.",
        "What is a p-value and how do you interpret it?",
        "Describe how you would handle missing data in a dataset.",
        "What is the difference between correlation and causation?",
        "Explain what A/B testing is and how you'd set one up.",
        "How would you identify outliers in a dataset?",
        "What SQL query would you write to find the top 5 customers by revenue?",
        "Explain what a pivot table is and when you'd use one.",
    ]
}

SCORING_PROMPT = """You are a strict but fair technical interview evaluator. Score the candidate's answer to the interview question below.

Role being interviewed for: {role}
Question: {question}
Candidate's Answer: {answer}

Evaluate on these 4 dimensions (each 0-10):
1. RELEVANCE: Did they answer the actual question asked?
2. CLARITY: Was the answer clear, structured, and easy to follow?
3. TECHNICAL_ACCURACY: Was the technical content correct and precise?
4. CONFIDENCE: Did the answer show confidence (avoid filler phrases like "I think maybe", "I'm not sure but")?

Return ONLY a valid JSON object with this exact structure:
{{
  "relevance": <float 0-10>,
  "clarity": <float 0-10>,
  "technical_accuracy": <float 0-10>,
  "confidence": <float 0-10>,
  "overall": <average of above>,
  "feedback": "<2-3 sentence overall feedback>",
  "keywords_matched": ["<key term 1>", "<key term 2>"],
  "improvement_tips": ["<tip 1>", "<tip 2>", "<tip 3>"]
}}"""

def get_questions(role: str, count: int = 5):
    import random
    questions = QUESTION_BANK.get(role, QUESTION_BANK["SDE"])
    return random.sample(questions, min(count, len(questions)))

def score_answer(role: str, question: str, answer: str) -> dict:
    prompt = SCORING_PROMPT.format(role=role, question=question, answer=answer)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    result = json.loads(raw.strip())
    # Ensure overall is recalculated
    dims = ["relevance", "clarity", "technical_accuracy", "confidence"]
    result["overall"] = round(sum(result[d] for d in dims) / 4, 2)
    return result
