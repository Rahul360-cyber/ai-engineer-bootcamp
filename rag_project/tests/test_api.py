from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from google.genai.errors import ServerError

client = TestClient(app)

def test_retrieve_endpoint():
    with patch("main.get_embedding_model") as mock_model,\
         patch("main.query_chunks") as mock_retrieval:
        mock_retrieval.return_value = [{
            "documents" : "RAG combines retrieval with generation.",
            "metadata" : { "SOURCE" : "test.pdf",
                           "page" : 0},
                         "distances" : 0.4
                          }]
        response = client.post("/retrieve", json = {"question" : "what is RAG?"})
        data = response.json()
        assert(response.status_code == 200)
        assert data["retrieved chunks"] == "RAG combines retrieval with generation."
        assert data["source"][0]["sources"] == "test.pdf"
        assert data["source"][0]["pages"] ==  0
        

         
def test_query_endpoint():
    with patch("main.get_embedding_model"),\
         patch("main.query_chunks") as mock_retrieval,\
         patch("main.get_gemini_client"),\
         patch("main.generate_answer") as mock_generation:
        mock_retrieval.return_value = [
            {
                "documents" : "RAG combines retrieval and generation",
                "metadata" : {
                    "SOURCE" : "test.pdf",
                    "page" : 0

                },
                "distance" : 0.4
            }
        ]
        mock_generation.return_value = ("RAG retrieves relevant information before generating an answer")
        response = client.post("/query",json = {"question" : "what is RAG"})
        data = response.json()
        assert (response.status_code == 200)
        assert data["question"] == "what is RAG"
        assert data["answer"] == "RAG retrieves relevant information before generating an answer"
        assert data["sources"][0]["sources"] == "test.pdf"


def test_agent_response():
    with patch("main.run_agent") as mock_run_agent:
        mock_run_agent.return_value=("the model uses a spectral compresson ...")
        response = client.post("/agent/query",json = {"question" :  "which architecture is my thesis"})
        data = response.json()
        assert(response.status_code == 200)
        assert data["question"] == "which architecture is my thesis"
        assert data["answer"] == "the model uses a spectral compresson ..."
        mock_run_agent.assert_called_once_with("which architecture is my thesis")


def test_agent_service_unavailable():
    with patch("main.run_agent") as mock_run_agent:
        mock_run_agent.side_effect = ServerError(503,{"error":{"code":503,"message":"service unavailable"}},
                                                 None)
        response = client.post("/agent/query",json = {"question" :  "which architecture is my thesis"})
        data = response.json()
        assert (response.status_code == 503)