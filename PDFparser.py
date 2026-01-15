# llama-parse is async-first, running the sync code in a notebook requires the use of nest_asyncio
import nest_asyncio
from llama_parse import LlamaParse
import os

nest_asyncio.apply()


parser = LlamaParse(
    api_key="",  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown",  # "markdown" and "json" are available
    num_workers=4, # if multiple files passed, split in `num_workers` API calls
    verbose=True,
    language="en", # Optionaly you can define a language, default=en
    parsing_instruction="""The provided document is a presentation slide deck.
    It could containg tables, images, diagrams and text. Extract the text content from the document. Output any math equation in LATEX markdown (between $$).
    For diagrams and images additionally decribe the visual content. Be as concise as possible. Multiple lives are at stake. You must get this right."""
)





def parse_pdf(file_path):
    documents = parser.load_data(file_path)
    #json_objs = parser.get_json_result(file_path)
    #json_list = json_objs[0]["pages"]
    return documents





if __name__ == "__main__":
    #get the path of the current file
    path = os.path.realpath(__file__)
    #construct the path to the PDF file
    path = os.path.dirname(path) + "/ChatGPT_BeyondtheHype.pdf"

    target_page = 20
    print(parse_pdf(path)[0].text.split("\n---\n")[target_page])