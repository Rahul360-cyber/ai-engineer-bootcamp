from sentence_transformers import SentenceTransformer
import numpy as np
import os
from google import genai
# import faiss
import re 
"""
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
"""
"""
print(embeddings.shape)
print(embeddings[0])
print(len(embeddings[0]))
print(embeddings[0].shape)
"""
"""
def retrieve_faiss(embeddings,question,chunk):
    dimension = embeddings.shape[1]
    embedding_faiss = embeddings.astype("float32")
    faiss.normalize_L2(embedding_faiss)
    index = faiss.IndexFlatIP(dimension)
    index.add(embedding_faiss)
    print (index.ntotal)
    q_embeddings = model.encode([question]).astype("float32")
    faiss.normalize_L2(q_embeddings)
    scores,indices = index.search(q_embeddings,3)
    print(scores)
    print(indices)
    top_chunks =[]
    for i,score in zip (indices[0],scores[0]):
        if score > 0.30:
           top_chunks.append(chunk[i])
        
    if not top_chunks:
        return       
    else:       
        return top_chunks 
"""
        
"""
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
     if s_score[index] > 0.80:
        top_chunks.append(chunk[index])
     elif not top_chunks:
             return "i dont know based on the provided context"
   return top_chunks

"""
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

def generate_answer(prompt,client):
        response = client.models.generate_content(model ="gemini-3.6-flash",contents = prompt)
        return response.text  

"""
if __name__ == "__main__":
    question = "What is the capital of Japan?"
        
    t_chunks = retrieve(question,embeddings,chunk,top_k = 3)
    t_chunks_ = retrieve_faiss(embeddings,question,chunk)
    
    context = "\n\n".join(t_chunks_)
    prompt = build_prompt(question,context)
    client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])
    print(generate_answer(prompt,client))
"""

def para_splitting(text):
    return  re.split(r"(?<=[.!?])\s+", text.strip())




def paragraph_wise_chunking(docs):
    current_chunks = ""
    paragraphs = []
    paragraphs = docs.split("\n\n")
    chunks =[]
    chunk_size = 1000
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > chunk_size:
            if current_chunks:
                chunks.append(current_chunks)
                current_chunks = ""
            smaller_chunks = sentence_chunking(para,chunk_size=chunk_size,overlap=200)
            chunks.extend(smaller_chunks)
            continue
        if current_chunks == "":
            current_chunks = para
        elif len(current_chunks)+ len("\n\n")+ len(para) <= chunk_size:
            current_chunks +="\n\n"+para
            
        else:
            chunks.append(current_chunks)
            if len(para) > chunk_size:
                  smaller_chunks = sentence_chunking(para,chunk_size=1000,overlap = 200)
                  chunks.extend(smaller_chunks)
                  continue
            sentences = para_splitting(current_chunks)
            overlap_para = sentences[-1]
            if len (overlap_para) + len("\n\n") + len(para) <= chunk_size:
                 current_chunks = overlap_para + "\n\n" + para
            else:
                 current_chunks = para
    if current_chunks:
        chunks.append(current_chunks)
    return chunks

def sentence_chunking(paragraph,chunk_size = 1000,overlap = 200):
        sentences = para_splitting(paragraph)
        chunks =[]
        current_sentences =[]

        for sentence in sentences:
            if len(sentence) > chunk_size:
                if current_sentences:
                    chunks.append(" ".join(current_sentences))
                    current_sentences = []

                small_se = split_long_sentences(
                    sentence,
                    chunk_size=chunk_size,
                    overlap=overlap
                )

                chunks.extend(small_se)
                continue
            proposed_chunk =  " ".join(current_sentences + [sentence])

            if len(proposed_chunk) <= chunk_size:
                current_sentences.append(sentence)
            else:
                chunks.append(" ".join(current_sentences))
                last_sentence = current_sentences[-1]
                if len(last_sentence) + 1 + len(sentence) <= chunk_size:
                    current_sentences = [last_sentence,sentence]
                else:
                    if len(sentence) > chunk_size:
                         chunks.extend((split_long_sentences(sentence)))
                         continue
                    current_sentences = [sentence]
        if current_sentences:
            chunks.append(" ".join(current_sentences))
        return chunks
 

def split_long_sentences(sentence,chunk_size =  1000,overlap = 200):
    if not 0 <= overlap < chunk_size:
        raise ValueError("ovelap must be smaller than chunk size")

    chunk = []
    start = 0

    while start < len(sentence):
        end = min(start + chunk_size,len(sentence))
        chunk.append(sentence[start:end])
        if end == len(sentence):
            break

        start = end - overlap

    return chunk


def chunk_pdf_pages(pages,source,chunk_size = 1000,overlap = 200):
         start = 0
         end = start + chunk_size
         final_chunk=[]
         for page in pages:
            start = 0
            text = page["text"]
            page_number = page["page"]
            chunks = paragraph_wise_chunking(text)
            for i in chunks:
                chunk_data ={
                    "text" : i,
                    "page" : page_number,
                    "source" : source
                            }
              
                final_chunk.append(chunk_data)
         return final_chunk

pages = [
    {
        "page": 0,
        "text": "Machine learning extracts patterns.\n\nNeural networks learn representations."
    },
    {
        "page": 1,
        "text": "Random forests combine multiple decision trees."
    }
]

result = chunk_pdf_pages(pages, "test.pdf")

print("Number of chunks:", len(result))

for chunk in result:
    print(chunk)
    print("Length:", len(chunk["text"]))