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
<paste your table: question, expected, result>

Corpus used: <PDF titles and sources>

## Limitations
- Tested manually on 8 questions; there is no formal evaluation yet
- Chunks never span pages, so ideas split across a page break can be missed
- Scanned PDFs are not supported (no OCR)
- Pure vector search can miss exact keywords

## What's next
A systematic evaluation (labeled question set, retrieval and answer-quality metrics),
hybrid search, and a simple UI.
