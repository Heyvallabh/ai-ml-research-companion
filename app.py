import os
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from openai import OpenAI
import hashlib
import re

NOT_FOUND = "I couldn't find this in the provided documents."

from dotenv import load_dotenv
load_dotenv() 


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "openai/gpt-oss-120b"
model = SentenceTransformer("all-MiniLM-L6-v2")

folder_path = "Documents"
files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

Documents = []
Chunks = []

############################################################################################
# Reading files and chunking process
for file in files:
    reader = PdfReader(f"{folder_path}/{file}")
    Document = []

    for page in reader.pages:
        text = page.extract_text()
        Document.append(text)
    Documents.append((file,Document))

    
for file,Document in Documents:
    for page_no, page in enumerate(Document,start=1):
        splitted = page.split()
        total_words = len(splitted)

        if total_words < 25:
            continue

        overlap = 30
        chunk_size = 150
        step = chunk_size - overlap

        for idx, i in enumerate(range(0,total_words,step)):
            Chunk_list = splitted[i:i + chunk_size]
            chunk_piece = " ".join(Chunk_list).strip()

            # Create a unique text anchor for this specific chunk
            unique_string = f"{file}_p{page_no}_c{idx}"
            deterministic_id = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

            Chunks.append(
                {
                    "id": deterministic_id,  # Use the new stable ID
                    "Chunk_piece": chunk_piece,
                    "metadata": {"Page no" : page_no ,"PDF":file , "Page_chunk_index":idx , "Unique_ID":deterministic_id},
                }  
            )
            if i + chunk_size >= len(splitted):
                break

############################################################################################
# Storing chunks and metadata into CHROMADB

# CHROMA_client = chromadb.Client()
# collection = CHROMA_client.get_or_create_collection(name="AIML_Companion",metadata={"hnsw:space": "cosine"})

CHROMA_client = chromadb.PersistentClient(path="./chroma_db")
collection = CHROMA_client.get_or_create_collection(name="AIML_Companion", metadata={"hnsw:space": "cosine"})

# ids = [c["metadata"]["chunk_index"] for c in Chunks]
ids = [c["id"] for c in Chunks]
documents = [c["Chunk_piece"] for c in Chunks]
metadatas = [c["metadata"] for c in Chunks]

embeddings = model.encode(documents).tolist()

collection.upsert(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)
print("chunks this run:", len(Chunks), "| stored in DB:", collection.count())


############################################################################################
# Querying and retriving relevant chunks from CHROMADB
query_text = "Why did the authors randomize the order of the distractor documents?"
query_embedding = model.encode(query_text,normalize_embeddings=True).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=5
)
############################################################################################
# Prompt construction + Context injection
def build_prompt():
    context = "\n\n".join(
        f"[{n}] (PDF: {m['PDF']}, page {m['Page no']})\n{d}"
        for n, (d, m) in enumerate(zip(results["documents"][0], results["metadatas"][0]), start=1)
    ) 

    system = f"""You are a research assistant. Answer ONLY using the numbered passages given by the user.
    - Never add facts from your own knowledge, even if you know them.
    - Explain in a clear, conversational way, like teaching a learner. Do not just copy sentences.
    - Put a citation at the end of EVERY sentence, using plain square brackets and the passage number: [1] or [2][3].
    - Passages may contain their own citations such as (Dai et al., 2019). Do NOT copy those. Cite only with passage numbers.
    Then add at most one sentence about what the passages do cover."""
    user = f"Passages:\n\n{context}\n\nQuestion: {query_text}"

    # print("User content : " + user)


    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

############################################################################################
# Making final call to LLM and printing final response + Citation
response = client.chat.completions.create(
    model=MODEL,
    messages=build_prompt(),
    temperature=0.2
)

print("\n This is the final response : \n")
answer = (response.choices[0].message.content or "").strip()
answer = answer.replace("【", "[").replace("】", "]")
print(answer)

normalized_list = results["metadatas"][0]

if answer.lower().replace("\u2019", "'").startswith(NOT_FOUND.lower()):
    print("\n No citations: the answer was not found in the documents.")
else:
    cited = []
    for group in re.findall(r"\[([\d,\s]+)\]", answer):    # text inside every [...]
        for number in re.findall(r"\d+", group):           # the digits inside it
            number = int(number)
            if number not in cited:
                cited.append(number)

    for number in cited:
        if 1 <= number <= len(normalized_list):
            data = normalized_list[number - 1]
            print(f"\n This is citation : [{number}] PDF : {data['PDF']} , Page no : {data['Page no']} ,  Page chunk index : {data['Page_chunk_index']}")
        else:
            print(f"\n Warning: the model cited [{number}], which does not exist")

    if len(cited) == 0:
        print("\n Warning: the answer has no citations, treat it as unverified.")
    

############################################################################################
# 5 Simple Steps :
# 1) Reading files and chunking process
# 2) Storing chunks and metadata into CHROMADB
# 3) Querying and retriving relevant chunks from CHROMADB
# 4) Prompt construction + Context injection
# 5) Making final call to LLM and printing final response + Citation