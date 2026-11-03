
from vector_store import query_chunks,load_pdf,chunk_pdf_pages,create_embeddings,store_chunks,document_exists,meta_data_exists,delete_document_source,same_documents_version,collection
import os
from utils import get_file_hash

def ingest_pdfs(pdf_filess,model,CHUNKER_VERSION):
    for i in pdf_filess:
        path = i
        source = os.path.basename(path)
        file_hash = get_file_hash(path)
        if same_documents_version(source,file_hash,CHUNKER_VERSION):
            print(f"{source} already exists.skipping")
            continue
        if document_exists(source):
            delete_document_source(source)
        text = load_pdf(path)
       
        for page in text:
            print(
                  "PAGE:", page["page"],
                  "TEXT LENGTH:", len(page["text"]) if page["text"] else 0
                 )
            print(
                 "PREVIEW:",
                 repr(page["text"][:100]) if page["text"] else "NO TEXT"
                 )
        print("source:",source)
        print("pages:", len(text))

        chunk = chunk_pdf_pages(text, source)
        print("chunks:",len(chunk))

        embeddings = create_embeddings(model,chunk)
        print("EMBEDDINGS SHAPE:", embeddings.shape)
        store_chunks(chunk,embeddings,file_hash,CHUNKER_VERSION)