import pytest

from rag import paragraph_wise_chunking

@pytest.mark.parametrize("text",[
    "Machine learning is useful.",
    "a" * 1500,
    "",
    "a"*1000,
    "hi this side Rahul","i am an upcoming Ai engineer."
])
def test_paragraph_wise_chunking(text):

         
    result = paragraph_wise_chunking(text)
    if text == "":
        assert (result == [])
    else:
        assert (len(result)>0)
    assert all( chunk!="" for chunk in result)
    assert all(len(chunk) >0 and len(chunk) <= 1000 for chunk in result)
    assert all(isinstance(chunk,str) for chunk in result )
