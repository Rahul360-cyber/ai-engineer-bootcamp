from unittest.mock import patch
from ingestion import ingest_pdfs
import numpy as np
def test_ingestion():
    with patch("ingestion.get_file_hash",return_value = "abc123"),\
         patch("ingestion.same_documents_version",return_value = True),\
         patch("ingestion.create_embeddings") as mock_embeddings:
         ingest_pdfs(pdf_filess=["test.pdf"],
                    model=None,
                    CHUNKER_VERSION="semantic_v1")
         mock_embeddings.assert_not_called()
def test_ingestion2():
     with patch("ingestion.get_file_hash",return_value ="abc123"),\
          patch("ingestion.same_documents_version",return_value = False),\
          patch("ingestion.document_exists",return_value =  True),\
          patch("ingestion.load_pdf") as mock_loading_pdf,\
          patch("ingestion.chunk_pdf_pages") as mock_chunk_pdf_pages,\
          patch("ingestion.create_embeddings") as mock_embeddings,\
          patch("ingestion.delete_document_source") as mock_deletion,\
          patch("ingestion.store_chunks") as mock_storage:
          ingest_pdfs(pdf_filess=["test.pdf"],
                    model=None,
                    CHUNKER_VERSION="semantic_v1")
          mock_chunk_pdf_pages.return_value = [{"text": "Machine learning is useful", "page": 0, "source": "test.pdf"}]
          mock_loading_pdf.return_value = [{"page":0,"text":"Machine learning is useful"}]
          mock_embeddings.return_value = np.array([[0.1,0.2,0.3]])
          mock_deletion.assert_called_once()
          mock_storage.assert_called_once()
