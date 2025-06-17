import lmstudio as lms
from pick import pick
import os
from PyPDF2 import PdfReader
import time

def modelpicker():
    # Lets the user pick a model from all available llms in lmstudio
    title = 'Pick a model to use as a main (smart) model, it doesnt need to be able to accept images:'
    models = lms.list_downloaded_models("llm")
    options = [model.model_key for model in models]
    option, index = pick(options, title)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Loading model: {option}")
    with lms.Client() as client:
        global mainmodel
        mainmodel = client.llm.load_new_instance(option)
        print(f"Model {option} loaded successfully.")
        print(f"TIP: When loading a model for the first time, go into LM-Studio and set the context length to the highest value possible for the model, this will allow you to analyze larger papers.")
        time.sleep(1)  # Wait for a second to let the user read the message
    return

def paperpicker():
    # Lets the user pick a paper from papers/
    title = 'Pick a paper to analyze:'
    papers = os.listdir('papers')
    options = [paper for paper in papers if paper.endswith('.pdf')]
    option, index = pick(options, title)
    return option

def tokencount_paper(paper):
    # Counts the number of tokens in a paper
    import PyPDF2
    with open(f'papers/{paper}', 'rb') as f:
        reader = PdfReader(f)
        content = ""
        for page in reader.pages:
            content += page.extract_text() or ""
    model = lms.llm()
    tokens = len(model.tokenize(content))
    return tokens

def respond_stream(prompt, paper):
    with open(f'papers/{paper}', 'rb') as f:
            reader = PdfReader(f)
            content = ""
            for page in reader.pages:
                content += page.extract_text() or ""
    with lms.Client() as client:
        model = client.llm.model()
        print(f"This may take a while to start, depending on the model and paper size. You can see the progress in the LM-Studio console in the developer tab.")

        current_buffer = "" 
        in_think_content_mode = False   # for thinking models, do not change this
        think_tag_open = "<think>"      # tags for thinking models, change this if your model uses different tags
        think_tag_close = "</think>"
        grey_code = "\033[90m"
        reset_code = "\033[0m"
            
        final_response_text = ""

        if os.name == 'nt':
            os.system('')

        for fragment in model.respond_stream(prompt):
            current_buffer += fragment.content
                
            processed_text_for_fragment = ""
            text_for_final_response = ""

            while True:
                if not in_think_content_mode:
                    open_tag_index = current_buffer.find(think_tag_open)
                    if open_tag_index != -1:
                        text_to_add = current_buffer[:open_tag_index]
                        processed_text_for_fragment += text_to_add
                        text_for_final_response += text_to_add
                            
                        processed_text_for_fragment += grey_code
                        current_buffer = current_buffer[open_tag_index + len(think_tag_open):]
                        in_think_content_mode = True 
                    else:
                        processed_text_for_fragment += current_buffer
                        text_for_final_response += current_buffer
                        current_buffer = ""
                        break
                else: 
                    close_tag_index = current_buffer.find(think_tag_close)
                    if close_tag_index != -1:
                        processed_text_for_fragment += current_buffer[:close_tag_index]
                        processed_text_for_fragment += reset_code
                        current_buffer = current_buffer[close_tag_index + len(think_tag_close):]
                        in_think_content_mode = False
                    else:
                        processed_text_for_fragment += current_buffer
                        current_buffer = ""
                        break
                
            if processed_text_for_fragment:
                print(processed_text_for_fragment, end="", flush=True)
            if text_for_final_response:
                final_response_text += text_for_final_response

        if current_buffer:
            if not in_think_content_mode:
                final_response_text += current_buffer
            print(current_buffer, end="", flush=True)

        if in_think_content_mode:
                print(reset_code, end="", flush=True)

        print() 
        os.system('cls' if os.name == 'nt' else 'clear')
        print(final_response_text.strip())
        return final_response_text.strip()


def summerize_paper(paper):
    # Summarizes the paper using the main model
    title = 'Do you want a short summary of the paper?'
    options = ['Yes', 'No']
    _, index = pick(options, title)
    if index == 0:
        with open(f'papers/{paper}', 'rb') as f:
            reader = PdfReader(f)
            content = ""
            for page in reader.pages:
                content += page.extract_text() or ""
        with lms.Client() as client:
            model = client.llm.model()
            print(f"Summarizing... \nThis may take a while to start, depending on the model and paper size. You can see the progress in the LM-Studio console in the developer tab.")
            prompt = f"Summarize this paper:\\n{content}"

            current_buffer = "" 
            in_think_content_mode = False   # for thinking models, do not change this
            think_tag_open = "<think>"      # tags for thinking models, change this if your model uses different tags
            think_tag_close = "</think>"
            grey_code = "\033[90m"
            reset_code = "\033[0m"
            
            final_summary_text = ""

            if os.name == 'nt':
                os.system('')

            for fragment in model.respond_stream(prompt):
                current_buffer += fragment.content
                
                processed_text_for_fragment = ""
                text_for_final_summary = ""

                while True:
                    if not in_think_content_mode:
                        open_tag_index = current_buffer.find(think_tag_open)
                        if open_tag_index != -1:
                            text_to_add = current_buffer[:open_tag_index]
                            processed_text_for_fragment += text_to_add
                            text_for_final_summary += text_to_add
                            
                            processed_text_for_fragment += grey_code
                            current_buffer = current_buffer[open_tag_index + len(think_tag_open):]
                            in_think_content_mode = True 
                        else:
                            processed_text_for_fragment += current_buffer
                            text_for_final_summary += current_buffer
                            current_buffer = ""
                            break
                    else: 
                        close_tag_index = current_buffer.find(think_tag_close)
                        if close_tag_index != -1:
                            processed_text_for_fragment += current_buffer[:close_tag_index]
                            processed_text_for_fragment += reset_code
                            current_buffer = current_buffer[close_tag_index + len(think_tag_close):]
                            in_think_content_mode = False
                        else:
                            processed_text_for_fragment += current_buffer
                            current_buffer = ""
                            break
                
                if processed_text_for_fragment:
                    print(processed_text_for_fragment, end="", flush=True)
                if text_for_final_summary:
                    final_summary_text += text_for_final_summary

            if current_buffer:
                if not in_think_content_mode:
                    final_summary_text += current_buffer
                print(current_buffer, end="", flush=True)

            if in_think_content_mode:
                 print(reset_code, end="", flush=True)

            print() 
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Summary:\n")
            print(final_summary_text.strip())
            
    else:
        return



def main():
    model = lms.llm()
    os.system('cls' if os.name == 'nt' else 'clear')
    paper = paperpicker()
    print(f"Selected paper: {paper}")
    token_count = tokencount_paper(paper)
    model_context_length = model.get_context_length()
    if token_count > model_context_length:
        print(f"Warning: The paper has {token_count} tokens, which exceeds the model's context length of {model_context_length} tokens. Extend the context length in the model settings in LM-Studio or load a different model.")
    else:
        print(f"Token count for '{paper}': {token_count}")
    user_input = input("Ask a question about the paper: ")
    respond_stream(user_input, paper)



if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    modelpicker()
    title = 'Do you want to load a vision model to turn images into text for the main model?'
    options = ['Yes(not yet implemented)', 'No']
    option, index = pick(options, title)
    if index == 0:
        print("Vision model loading is not yet implemented.")
    else:
        print("No vision model will be loaded.")
    main()