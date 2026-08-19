from sentence_transformers import SentenceTransformer
import numpy as np
import os
from google import genai
path ="data/sample.txt"
def load_docs(path):
    with open (path,"r",encoding ="utf-8") as file:
       text = file.read()
    return text

docs = load_docs(path)
def chunk_text(docs):
    chunk_size = 500
    overlap = 50
    l = len(docs)
    start = 0
    chunks = []
    while start < l:
        end = start + chunk_size
        chunks.append(docs[start:end])
        start = end - overlap
    return chunks

chunk = chunk_text(docs)
model = SentenceTransformer("sentence-transformers/all-Minilm-l6-v2")

def create_embeddings(chunk,model):
   embeddings_ = model.encode(chunk)
   return embeddings_
embeddings = create_embeddings(chunk,model)
print(embeddings.shape)
print(embeddings[0])
print(len(embeddings[0]))
print(embeddings[0].shape)




def retrieve(question,embeddings,chunk,top_k = 3):
   s_score =[]
   q_embedding = model.encode(question)
   for i in range(len(embeddings)):
        cos = np.dot(q_embedding,embeddings[i])/(np.linalg.norm(q_embedding)*np.linalg.norm(embeddings[i]))
        s_score.append(cos)

   ranked_indices = np.argsort(s_score)[::-1]
   print(ranked_indices[0:top_k])
   for index in ranked_indices[0:top_k]:
       print("SCORE:", s_score[index])
       print("CHUNK:")
       print(chunk[index])
       print("-" * 50)

   top_chunks = []

   for index in ranked_indices[:top_k]:
     top_chunks.append(chunk[index])
   return top_chunks


if __name__ == "__main__":
    question = "What is the capital of Japan?"
        
    t_chunks = retrieve(question,embeddings,chunk,top_k = 3)
    context = "\n\n".join(t_chunks)

    def build_prompt(question,context):
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
        return prompt
    prompt = build_prompt(question,context)
    client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])
    def generate_answer(prompt,client):
        response = client.models.generate_content(model ="gemini-3.6-flash",contents = prompt)
        return response.text  
    print(generate_answer(prompt,client))
