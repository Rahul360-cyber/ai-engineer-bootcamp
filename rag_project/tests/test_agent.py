from unittest.mock import patch, MagicMock
from agent import run_agent_manually
from _pytest.python import CallSpec2
from google.genai import types

def test_agent_direct_answer():
   with patch.dict("os.environ",{"GEMINI_API_KEY":"fake_test_key"}):
    with patch("agent.genai.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.function_calls = None
        mock_response.text = "The answer is 42."
        mock_client.return_value.models.generate_content.return_value = mock_response
        result = run_agent_manually("what is the answer?")
        assert result == "The answer is 42."
        mock_client.return_value.models.generate_content.assert_called_once()

def test_agent_execution():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_test_key"}):
        with patch("agent.genai.Client") as mock_client:
            with patch("agent.search_documents") as mock_search:

                # First response: Gemini requests document retrieval
                function_call = MagicMock()
                function_call.name = "search_documents"
                function_call.args = {
                    "query": "hyperspectral architecture"
                }

                first_response = MagicMock()
                first_response.function_calls = [function_call]

                first_response.candidates[0].content = types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="search_documents",
                            args={
                                "query": "hyperspectral architecture"
                            }
                        )
                    ]
                )

                # Second response: Gemini produces its answer
                second_response = MagicMock()
                second_response.function_calls = None
                second_response.text = (
                    "the thesis uses a spectral compressor and VIT"
                )

                # Simulate two consecutive Gemini responses
                mock_generate = (
                    mock_client.return_value.models.generate_content
                )

                mock_generate.side_effect = [
                    first_response,
                    second_response
                ]

                # Simulate ChromaDB retrieval
                mock_search.return_value = (
                    "the model uses a spectral compressor and VIT."
                )

                result = run_agent_manually(
                    "what architecture did my thesis use"
                )

                assert result == (
                    "the thesis uses a spectral compressor and VIT"
                )

                mock_search.assert_called_once_with(
                    "hyperspectral architecture"
                )

                assert mock_generate.call_count == 2

                # Verify the second Gemini call includes the tool result
                second_call_history = mock_generate.call_args_list[1].kwargs[
                    "contents"
                ]

                assert len(second_call_history) == 3
                assert second_call_history[1].role == "model"
                assert second_call_history[2].role == "tool"

import pytest
from unittest.mock import patch, MagicMock
from google.genai import types


def test_agent_max_iterations():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_test_key"}):
        with patch("agent.genai.Client") as mock_client:
            with patch("agent.search_documents") as mock_search:

                # 1. Simulate Gemini requesting the retrieval tool
                function_call = MagicMock()
                function_call.name = "search_documents"
                function_call.args = {
                    "query": "what is the architecture of the model?"
                }

                # 2. Create a mocked Gemini response
                mock_response = MagicMock()
                mock_response.function_calls = [function_call]

                mock_response.candidates[0].content = types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="search_documents",
                            args=function_call.args
                        )
                    ]
                )

                # 3. Gemini repeatedly requests the same tool
                mock_generate = (
                    mock_client.return_value.models.generate_content
                )
                mock_generate.return_value = mock_response

                # 4. Mock the retrieval result
                mock_search.return_value = "Retrieved document content."

                # 5. Verify that the iteration limit raises an error
                with pytest.raises(
                    RuntimeError,
                    match="maximum tool-execution rounds reached"
                ):
                    run_agent_manually(
                        "Search my thesis repeatedly"
                    )

                # 6. Verify the execution budget
                assert mock_generate.call_count == 5
                assert mock_search.call_count == 5