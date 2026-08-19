from sentence_transformers import SentenceTransformer
import numpy as np
import os
from google import genai
with open ("data/sample.txt","r",encoding ="utf-8") as file:
    text = file.read()

model = SentenceTransformer("sentence-transformers/all-Minilm-l6-v2")

def chunk_text(text):
    chunk_size = 500
    overlap = 50
    l = len(text)
    start = 0
    chunks = []
    while start < l:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
chunk = chunk_text(text)
embeddings = model.encode(chunk)
print(embeddings.shape)
print(embeddings[0])
print(len(embeddings[0]))
print(embeddings[0].shape)

question = "What is the capital of Japan?"
q_embedding = model.encode(question)
s_score =[]
for i in range(len(embeddings)):
        cos = np.dot(q_embedding,embeddings[i])/np.linalg.norm(q_embedding)*np.linalg.norm(embeddings[i])
        s_score.append(cos)

ranked_indices = np.argsort(s_score)[::-1]
print(ranked_indices[0:3])
for index in ranked_indices[0:3]:
    print("SCORE:", s_score[index])
    print("CHUNK:")
    print(chunk[index])
    print("-" * 50)

top_chunks = []

for index in ranked_indices[:3]:
     top_chunks.append(chunk[index])

context = "\n\n".join(top_chunks)

prompt = f"""
Answer the question only using the context below,

if the answer is not present in the context, say:
    "say i dont know based on the provided context."

context:
{context}

Question:
{question}
    """

print(prompt)

client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(model ="gemini-3.6-flash",contents = prompt)
print(response.text)