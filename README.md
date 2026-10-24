# AI/ML Research Companion

A command-line RAG assistant that answers questions **only from your PDF documents**,
cites the PDF and page it used, and says so when the answer isn't in the documents.
Built without a RAG framework, to understand every step.

## How it works
1. Read PDFs and split each page into overlapping 150-word chunks (30-word overlap)
2. Embed the chunks with `all-MiniLM-L6-v2` and store them in ChromaDB (saved to disk)
3. Embed the question and retrieve the 5 most similar chunks
4. Build a prompt with numbered passages [1]-[5] and strict grounding rules
5. Call the LLM (`gpt-oss-20b` via Groq), then show only the passages it actually cited

## Design decisions
- Re-running never creates duplicates: each chunk has a stable id and is upserted.
- The prompt gives the model an exact refusal sentence, and the code detects it.
- Citations are parsed from the answer and checked against the retrieved passages.

## Setup
pip install -r requirements.txt
Copy .env.example to .env and add your GROQ_API_KEY
Put PDFs in Documents/, set query_text in main.py
python main.py

## Example (real output)
Question: "What is attention?" (the loaded paper is about long-context behavior)
Answer: "I couldn't find this in the provided documents. The passages discuss
distractor ordering and evaluation in multi-document QA."

## Manual smoke test
## Manual smoke test

| # | Type | Question | Expected | Result | Note |
|---|---|---|---|---|---|
| 1 | Answerable | What metric do the authors use to evaluate multi-document QA? | p.3 | ✅ |The answer matches the key, and the [2] citation points to a page that really contains it, and nothing is invented |
| 2 | Answerable | Why did the authors randomize the order of the distractor documents? | p.3, p.14 | ✅ | The answer matches the key, and the [4] citation points to a page that really contains it, and nothing is invented|
| 3 | Answerable | What happens to model performance when the distractors are hard negatives? | p.14 | ✅ | The answer matches the key, and the [1][2] citation points to a page that really contains it, and nothing is invented|
| 4 | Answerable | What instruction did the authors use to tell the model the search results were randomly ordered? | p.14 | ✅ |The answer matches the key, and the [3][2] citation points to a page that really contains it, and nothing is invented |
| 5 | Answerable | Which dataset is the multi-document QA task built from? | p.3 | ✅ |The answer matches the key, and the [4][1] citation points to a page that really contains it, and nothing is invented |
| 6 | Answerable | Where in the input context do models perform best, and where worst? | p.1 (abstract) | ✅ | The answer matches the key, and the [1][5] citation points to a page that really contains it, and nothing is invented|
| 7 | Answerable | Which two tasks do the authors use to study how models use long contexts? | p.1 (abstract) | ✅ |The answer matches the key, and the [1][3] citation points to a page that really contains it, and nothing is invented |
| 8 | Unanswerable | What is attention? | refusal | ✅ | refused correctly |
| 9 | Unanswerable | How do I bake bread? | refusal | ✅ | refused correctly |
| 10 | Unanswerable | What is gradient descent? | refusal | ✅ | refused correctly |

## Limitations
- Tested manually on 8 questions; there is no formal evaluation yet
- Chunks never span pages, so ideas split across a page break can be missed
- Scanned PDFs are not supported (no OCR)
- Pure vector search can miss exact keywords

## What's next
A systematic evaluation (labeled question set, retrieval and answer-quality metrics),
hybrid search, and a simple UI.