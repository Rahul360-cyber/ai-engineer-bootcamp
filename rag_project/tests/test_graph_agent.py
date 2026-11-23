from unittest.mock import MagicMock, patch

from google.genai import types
from graph_agent import graph


def make_direct_response(answer):
    response = MagicMock()
    response.function_calls = None
    response.text = answer
    return response


def make_tool_response(query):
    response = MagicMock()

    function_call = MagicMock()
    function_call.name = "search_documents"
    function_call.args = {"query": query}

    response.function_calls = [function_call]

    response.candidates[0].content = types.Content(
        role="model",
        parts=[
            types.Part.from_function_call(
                name="search_documents",
                args={"query": query},
            )
        ],
    )

    return response


def initial_state(question):
    return {
        "question": question,
        "messages": [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=question)],
            )
        ],
        "answer": "",
        "pending_tool": None,
        "tool_rounds": 0,
    }


def test_graph_direct_answer():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("graph_agent.genai.Client") as mock_client:
            with patch("graph_agent.search_documents") as mock_search:

                mock_generate = (
                    mock_client.return_value.models.generate_content
                )

                mock_generate.return_value = make_direct_response(
                    "RAG means Retrieval-Augmented Generation."
                )

                result = graph.invoke(initial_state("What is RAG?"))

                assert result["answer"] == (
                    "RAG means Retrieval-Augmented Generation."
                )

                assert result["tool_rounds"] == 0
                mock_search.assert_not_called()
                mock_generate.assert_called_once()


def test_graph_tool_execution():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("graph_agent.genai.Client") as mock_client:
            with patch("graph_agent.search_documents") as mock_search:

                mock_generate = (
                    mock_client.return_value.models.generate_content
                )

                mock_generate.side_effect = [
                    make_tool_response("hyperspectral thesis architecture"),
                    make_direct_response(
                        "The model uses a spectral compressor and ViT."
                    ),
                ]

                mock_search.return_value = (
                    "The thesis describes a spectral compressor and ViT."
                )

                result = graph.invoke(
                    initial_state("What architecture does my thesis use?")
                )

                assert result["answer"] == (
                    "The model uses a spectral compressor and ViT."
                )

                assert result["tool_rounds"] == 1
                assert result["pending_tool"] is None

                mock_search.assert_called_once_with(
                    "hyperspectral thesis architecture"
                )

                assert mock_generate.call_count == 2

                # The second Gemini request must include the tool result
                second_call = mock_generate.call_args_list[1]
                messages = second_call.kwargs["contents"]

                assert len(messages) == 3
                assert messages[1].role == "model"
                assert messages[2].role == "tool"


def test_graph_max_tool_calls():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("graph_agent.genai.Client") as mock_client:
            with patch("graph_agent.search_documents") as mock_search:

                mock_generate = (
                    mock_client.return_value.models.generate_content
                )

                mock_generate.return_value = make_tool_response(
                    "hyperspectral architecture"
                )

                mock_search.return_value = "Retrieved document content."

                result = graph.invoke(
                    initial_state("Search my thesis repeatedly"),
                    config={"recursion_limit": 20},
                )

                assert result["tool_rounds"] == 5
                assert result["answer"] == (
                    "Stopped: maximum tool_call limit reached."
                )

                assert mock_search.call_count == 5
                assert mock_generate.call_count == 6