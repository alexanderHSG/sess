import gradio as gr
import featureExtractorPDF
import lime
import lime.lime_tabular
import pandas as pd
import numpy as np
import pickle
import lime
import lime.lime_tabular
import sqlite3
import gradioQualityDimensionWrapper
import time
import os
import fitz  # Import PyMuPDF
from PIL import Image
import tempfile
import requests
import base64
import io
import nest_asyncio
from llama_parse import LlamaParse
import asyncio
from gradio_client import Client as grClient
import json
import urllib.parse
import time
from langchain_openai import OpenAI

from datasets import load_dataset
from huggingface_hub import login
from huggingface_hub import Repository


#os.system("pip uninstall -y gradio") 
#os.system("pip install gradio==4.31.0")




def explain_prediction():
    
    #repo = Repository(
     #   local_dir="DBss",
     #   repo_type="dataset",
     #   clone_from="ale979/all_slides",
     #   token=True
    #)
    #repo.git_pull(lfs = True)

    #read df from sql db
    conn = sqlite3.connect("all_talks.db")
    df = pd.read_sql_query("SELECT * FROM filtered_speakerdeckfeatures", conn)

#make time_elapsed_until_Oct23 0 if it is negative
    df['time_elapsed_until_Oct23'] = df['time_elapsed_until_Oct23'].apply(lambda x: 0 if x < 0 else x)

#filter for column content non null
    df = df[df['content'].notnull()]

#exclude slides with pictures text ratio more than 2
    df = df[(df['total_numImages']/df['total_numWords']) < 2]

#drop columns speaker, id, url, pdf
    df = df.drop(['url', 'pdf'], axis=1)

#filter for speaker with more than 20 entries only subsume other as other
    df['speaker'] = df['speaker'].apply(lambda x: x if len(df[df['speaker'] == x]) > 20 else 'other')

#filter for category with more than 20 entries only show category
    df = df[df.groupby('category').category.transform(len) > 20]

#exclude views equal to 0
    df = df[df['views'] != 0]

#dummy encoding for speaker and category
    df = pd.get_dummies(df, columns=['speaker', 'category'])

#make views log
    df['views'] = np.log(df['views'] + 0.1)

#order columns alphabetically
    df = df.reindex(sorted(df.columns), axis=1)

#20% test data
    test_data = df.sample(frac=0.2, random_state=1)
#20% validation data, make sure no overlap with test data
    df = df.drop(test_data.index)
    validation_data = df.sample(frac=0.25, random_state=1)
#60% train data
    df = df.drop(validation_data.index)
    train_data = df
    #get names of boolean columns
    bool_columns = train_data.select_dtypes(include='bool').columns.tolist()
    #get all feature names
    feature_names = train_data.columns.tolist()
    #drop id, stars, views, content in list
    feature_names = [x for x in feature_names if x not in ['id', 'stars', 'views', 'content']]

    #train_data = train_data.drop(['id', 'stars', 'views', 'content']
    cleaned_train_data = train_data.drop(['id', 'stars', 'views', 'content'], axis=1)
    cleaned_train_data = cleaned_train_data.to_numpy()

    explainer = lime.lime_tabular.LimeTabularExplainer(cleaned_train_data, feature_names=feature_names, class_names=['views'], categorical_features=bool_columns, verbose=True, mode='regression')

    return explainer


def process_pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        time.sleep(0.1)  # Sleep for a short while to avoid overloading the CPU
        page = doc.load_page(page_num)  # Load the current page
        pix = page.get_pixmap()  # Render page to an image
        img_data = pix.tobytes("ppm")  # Get the image data
        
        # Convert the binary data to an image using PIL
        image = Image.open(io.BytesIO(img_data))
        images.append(image)
    
    return images




#TODO
#def get_slide_cohesion(content):
#    api_key = os.getenv("OpenAI")
#    headers = {
#        "Content-Type": "application

async def check_factuality(file_path):
    print("starting factuality check...")

    parser = LlamaParse(
        #key set in env as LLAMA_CLOUD_API_KEY
        result_type="markdown",  # "markdown" and "text" are available
        num_workers=4, # if multiple files passed, split in `num_workers` API calls
        verbose=True,
        language="en", # Optionaly you can define a language, default=en
        parsing_instruction="""The provided document is a presentation slide deck. It could containg tables, images, diagrams and text. Extract the text content from the document. Output any math equation in LATEX markdown (between $$). For diagrams and images additionally decribe the visual content. Be as concise as possible. Multiple lives are at stake. You must get this right."""
    )
    nest_asyncio.apply()
    parsed_document = parser.load_data(file_path)
    client = grClient("IWIHSG/fact_check", hf_token= os.getenv("token"))
    print(parsed_document)
    result = client.predict(input_markdown=str(parsed_document), api_name = "/factuality_check")
    

    # Convert the JSON string to a Python dictionary
    try:
        result = json.loads(result)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        result = []

    markdown_output = "## Verification Results\n\n"
    # Start the markdown table with headers
    markdown_output += "| Statements Found in the Presentation | Verification Result | Link to Consensus Research Assistant and Google for Background Info |\n"
    markdown_output += "|--------------------------------------|:-------------------:|----------------------------------------------------|\n"

# Loop through each item and add it to the table
    for item in result:
        # Determine the emoji and link based on the verification result
        if item['verification_result'] == 'T' or item['verification_result'] == 'True':
            result_symbol = "✔️"
            link_consensus = ""
            link_google = ""
        else:
            result_symbol = "❌"
            encoded_searchString = urllib.parse.quote(item['searchString'])
            link_consensus = f"[Consensus](https://consensus.app/results/?q={encoded_searchString}&synthesize=on&copilot=on)"
            link_google = f"[Google](https://www.google.com/search?q={encoded_searchString})"
        #replace new lines for not breaking markdown formatting
        item['statement'] = item['statement'].replace('\n', ' ')
        # Format each row of the table
        markdown_output += f"| {item['statement']} | <span style='color:{'green' if item['verification_result'] == 'T' else 'red'};'>{result_symbol}</span> | {link_consensus} {link_google} |\n"

    print("factuality check done")
    return markdown_output




async def process_slide_deck(uploaded_file, category, prediction_days, author):    
    view_task = asyncio.create_task(calculate_views(uploaded_file, category, prediction_days, author))
    fact_task = asyncio.create_task(check_factuality(uploaded_file))

    fact_results = await fact_task
    qualityDimensionsHTML, predicted_views_html = await view_task
    return qualityDimensionsHTML, predicted_views_html, fact_results
    

class SlideFeedbackGenerator:
    """
    This module generates feedback for slides based on an image input.
    """
    def __init__(self, model_name="gpt-4o", api_key= os.getenv("OpenAI")):
        self.model_name = model_name
        self.api_key = api_key

    def process(self, selected_image):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        with open(selected_image, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        prompt_template = """provide a SHORT and concise prescriptive feedback on the slide. Avoid euphemistic feedback, be critical. Use the following question to guide your feedback, NOT all checkpoints at once need be applicable to this slide, consider wisely which one to recommend specifically. Do NOT just repeat the checkpoint descriptions. Additionally, if a checkpoint is applicable describe WHERE and HOW in the slide the checkpoints should implemented:
                        1. Insert a pictogram. Pictogram insertion can intuitively convey the slide content.
                        2. Add a subheading. Subheading addition makes the audiences convenient to find information.
                        3. Emphasize words. Emphasizing important words enhances a part of a text to make it noticeable.
                        4. Emphasize areas. Emphasizing important areas of the slides helps focus attention.
                        5. Add T1 and T2. Slide title (T1) and slide messages (T2) help the audiences more easily understand the main content of the exposition.
                        6. Use the grid structure. A grid structure helps organize target and comparison items in rows and columns, creating a table-like format.
                        7. Itemize the text. Text itemization is good in terms of readability and organization.
                        8. Add a comment. Comments aid in audiences’ understanding.
                        9. Correct flow. Left-to-right top-to-bottom flow mimics human scanning methods.
                        10. MECE. Mutually exclusive and collectively exhaustive (MECE) objects should be aligned without omissions and duplication to make the slides convincing. {content_category_prompt}"""
        content_category_prompt = """
                        11. Consistent formatting. Look for and point out inconsistencies.
                        12. Add an Action Title. Action titles make the audiences understand the key take-away easy and fast.
                        13. Citation style. Scientific sources are cited consistently via the same citation style."""
        prompt = prompt_template
        payload = {
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt
                    }, {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }]
            }],
            "max_tokens": 2048
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
        try:
            feedback = response['choices'][0]['message']['content']
        except KeyError:
            feedback = "Failed to obtain feedback. Please check the input or try again."
        return feedback

feedback_generator = SlideFeedbackGenerator(api_key = os.getenv("OpenAI"))


async def calculate_views(uploaded_file, category, prediction_days, author):    
    print("Starting view calculation...")
    
    # Extract features from the slide deck
    features = featureExtractorPDF.analyze_slidedeck_pdf(uploaded_file)
    features = pd.DataFrame([features], columns=features.keys())

    # Load the model
    with open('mlp_ensemble.sav', 'rb') as file:
        mlp_ensemble = pickle.load(file)
    #load svr.sav
    with open('svr.sav', 'rb') as file:
        svr = pickle.load(file)
    #load rfr_embeddings.sav
    with open('rfr_embeddings.sav', 'rb') as file:
        rfr_embeddings = pickle.load(file)

    #add dummy columns for category and author
    for c in ['Research', 'Technology', 'Business', 'Design', 'Storyboards', 'Science', 'How-to & DIY', 'Education', 'Programming', 'Marketing & SEO', 'Other']:
        features['category_' + c] = False
    
    for a in ['speaker_addyosmani', 'speaker_ajstarks', 'speaker_aleyda', 'speaker_ange', 'speaker_brainpadpr', 'speaker_cmaneu', 'speaker_cygames', 'speaker_dabeaz', 'speaker_daipresents', 'speaker_devnetnoord', 'speaker_dfm', 'speaker_doradora09', 'speaker_dotnetday', 'speaker_dunglas', 'speaker_eddie', 'speaker_eileencodes', 'speaker_elasticsearch', 'speaker_ericstoller', 'speaker_eueung', 'speaker_fixstars', 'speaker_fmunz', 'speaker_fr0gger', 'speaker_freee', 'speaker_gunnarmorling', 'speaker_hatena', 'speaker_heyitsmohit', 'speaker_hpgrahsl', 'speaker_inamiy', 'speaker_ivargrimstad', 'speaker_iwashi86', 'speaker_jamf', 'speaker_jennybc', 'speaker_jhellerstein', 'speaker_joergneumann', 'speaker_johtani', 'speaker_jollyjoester', 'speaker_kazupon', 'speaker_kishida', 'speaker_konakalab', 'speaker_konifar', 'speaker_kurochan', 'speaker_leastprivilege', 'speaker_lemiorhan', 'speaker_leriomaggio', 'speaker_letsconnect', 'speaker_libshare', 'speaker_linedevth', 'speaker_luxas', 'speaker_mamohacy', 'speaker_marcduiker', 'speaker_martinlippert', 'speaker_matleenalaakso', 'speaker_medley', 'speaker_mikecohn', 'speaker_mitsuhiko', 'speaker_miyakemito', 'speaker_mottox2', 'speaker_mploed', 'speaker_nihonbuson', 'speaker_nileshgule', 'speaker_no24oka', 'speaker_ocise', 'speaker_off2class', 'speaker_olivergierke', 'speaker_opelab', 'speaker_other', 'speaker_palkan', 'speaker_paperswelove', 'speaker_pauldix', 'speaker_pichuang', 'speaker_pixely', 'speaker_prof18', 'speaker_publicservicelab', 'speaker_pyama86', 'speaker_pycon2015', 'speaker_pycon2016', 'speaker_quasilyte', 'speaker_rachelhch', 'speaker_ramalho', 'speaker_redhatlivestreaming', 'speaker_reverentgeek', 'speaker_rmcelreath', 'speaker_rnakamuramartiny', 'speaker_rtechkouhou', 'speaker_sansanbuildersbox', 'speaker_senryakuka', 'speaker_shah', 'speaker_shlominoach', 'speaker_soudai', 'speaker_tagtag', 'speaker_takaking22', 'speaker_takashitanaka', 'speaker_tammielis', 'speaker_tenforward', 'speaker_thockin', 'speaker_thomasvitale', 'speaker_toshiseisaku', 'speaker_tosseto', 'speaker_uzulla', 'speaker_welcometomusic', 'speaker_wescale', 'speaker_yasuoyasuo', 'speaker_ymatsuwitter', 'speaker_yohhatu', 'speaker_yoshiakiyamasaki', 'speaker_ytaka23', 'speaker_ythecombinator', 'speaker_yuyumoyuyu', 'speaker_zoomquiet']:
        features[a] = False

    #categorical encoding category and author
    features['category_' + category] = True
    features[author] = True
    prediction_days = int(prediction_days)
    features['time_elapsed_until_Oct23'] = prediction_days
    #order the columns alphabetically
    features = features.reindex(sorted(features.columns), axis=1)

    #predict the number of views using svr_embeddings
    svr_predictions = svr.predict(features.drop(columns=['content']))

    explainer = explain_prediction()
    exp = explainer.explain_instance(features.drop(columns=['content']).iloc[0], svr.predict, num_features=400)

    sum = 0
    c = 0
    for i in exp.as_list():
        if i[0].startswith(author):
            sum += i[1]
            c += 1
    reputational_score = sum*3


    sum = 0
    c = 0
    for i in exp.as_list():
        #sum i[0] "numPages", "total_numImages", "std_numImages"
        if "numPages" in i[0] or 'total_numImages'in i[0] or 'std_numImages' in i[0]:
            sum += i[1]
            c += 1
    contextual_score = sum


    sum = 0
    c = 0
    for i in exp.as_list():
        if i[0].startswith('mean_numWords') or i[0].startswith('std_numWords') or i[0].startswith('total_numWords'):
            sum += i[1]
            c += 1

    representational_score = sum

    #predict the number of views using svr
    predicted_views = int(np.exp(svr_predictions[0])-0.1)
    # Predict the number of views using ensemble model
    #mlp_predictions = mlp_ensemble.predict(features)

    sum = 0
    c = 0
    for i in exp.as_list():
        if 'entropy' in i[0]:
            sum += i[1]
            c += 1
    intrinsic_score = sum
    print("Intrinsic score: ", intrinsic_score)

    qualityDimensionsHTML, predicted_views_html = gradioQualityDimensionWrapper.html_tranformer(predicted_views, intrinsic_score, contextual_score, representational_score, reputational_score)

    # Return the scores and the predicted number of views 
    return qualityDimensionsHTML, predicted_views_html


def asyncprocessing(uploaded_file, category, prediction_days, author):
    #Note: typical examples show using asyncio.run(), but that can only be called once per thread. Since this function can be called multiple times, creating and reusing the loop is what works
    try:
        import uvloop
        # Check if uvloop is the current loop policy
        if isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy):
            # Set to the default asyncio loop policy if uvloop is detected
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            print("uvloop was set, but reverted to asyncio's default loop policy.")
    except ImportError:
        # uvloop is not installed, proceed with the default asyncio loop
        print("uvloop not installed, using asyncio's default event loop.")

    try:
        # Check if there is a loop already running. If there is, reuse it.
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Explicitly create and set a new standard asyncio event loop if one is not running
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    #this sends the parameters to the function that sets up the async calls. Once all the calls to the API complete, it returns a list of the gr.Textbox with value= set.
    qualityDimensionsHTML, predicted_views_html, fact_results = loop.run_until_complete(process_slide_deck(uploaded_file, category, prediction_days, author))
    return qualityDimensionsHTML, predicted_views_html, fact_results

#def pop_up1():
#    gr.Info("Upload document in PDF format: Get started by uploading the slide deck you want to evaluate. Drag and drop your file here, or click to upload.")

def pop_up2():
    gr.Info("Choose a content category: Indicate the purpose for which you intend to publish the slide deck and the evaluation will be adjusted accordingly.")

def pop_up3():
    gr.Info("Select the author’s name: Select the author’s name to assign the slide deck to the author accordingly.")

def pop_up4():
    gr.Info("Customize your view prediction timeline: Choose how many days after upload you would like to predict the viewer engagement.")

def pop_up5():
    gr.Info("Enter ISCED-level of education of your audience: Indicate the educational degree of your audience to make the evaluation align with the educational aspiration.")

def pop_up6():
    gr.Info("Start to evaluate your slide deck: Based on your specified requirements and the uploaded slide deck, you can now start the AI-based evaluation.")

def pop_up7():
    gr.Info("Check the content of your slide deck: Verify the veracity of the content on the slides with our Google-powered factuality check.")

def pop_up8():
    gr.Info("Obtain an AI-driven assessment of your slide deck: Receive a comprehensive analysis expressed in clear, natural language. This tool evaluates your presentation's content, design, and overall effectiveness.")

with gr.Blocks() as demo_tab1:
    gr.Markdown("# Slide Deck Evaluation Dashboard")

    gr.Markdown("""
    Welcome to the Slide Deck Evaluation Dashboard, where advanced AI evaluates the content, design, and communication efficacy of your presentations. Enhance your insights with customized feedback, automated fact-checks, and AI-driven verification for unmatched accuracy and reliability. Simply upload your slide deck in PDF format, tailor your settings to suit your requirements, and start the evaluation. Explore our Single Slide Feedback for in-depth analysis of each slide.
    """)



    with gr.Row():
        upload = gr.File(label="Upload your slide deck", file_types=[".pdf"])
        #upload.change(lambda file_info: pop_up2(), inputs=[upload], outputs=[])
        
        
        category = gr.Dropdown(
            choices=['Research', 'Technology', 'Business', 'Design', 'Storyboards', 
                     'Science', 'How-to & DIY', 'Education', 'Programming', 
                     'Marketing & SEO', 'Other'],
            label="Content Category", value="Education"
        )
        
        author = gr.Dropdown(
            choices=['speaker_addyosmani', 'speaker_ajstarks', 'speaker_aleyda', 'speaker_ange', 'speaker_brainpadpr', 'speaker_cmaneu', 'speaker_cygames', 'speaker_dabeaz', 'speaker_daipresents', 'speaker_devnetnoord', 'speaker_dfm', 'speaker_doradora09', 'speaker_dotnetday', 'speaker_dunglas', 'speaker_eddie', 'speaker_eileencodes', 'speaker_elasticsearch', 'speaker_ericstoller', 'speaker_eueung', 'speaker_fixstars', 'speaker_fmunz', 'speaker_fr0gger', 'speaker_freee', 'speaker_gunnarmorling', 'speaker_hatena', 'speaker_heyitsmohit', 'speaker_hpgrahsl', 'speaker_inamiy', 'speaker_ivargrimstad', 'speaker_iwashi86', 'speaker_jamf', 'speaker_jennybc', 'speaker_jhellerstein', 'speaker_joergneumann', 'speaker_johtani', 'speaker_jollyjoester', 'speaker_kazupon', 'speaker_kishida', 'speaker_konakalab', 'speaker_konifar', 'speaker_kurochan', 'speaker_leastprivilege', 'speaker_lemiorhan', 'speaker_leriomaggio', 'speaker_letsconnect', 'speaker_libshare', 'speaker_linedevth', 'speaker_luxas', 'speaker_mamohacy', 'speaker_marcduiker', 'speaker_martinlippert', 'speaker_matleenalaakso', 'speaker_medley', 'speaker_mikecohn', 'speaker_mitsuhiko', 'speaker_miyakemito', 'speaker_mottox2', 'speaker_mploed', 'speaker_nihonbuson', 'speaker_nileshgule', 'speaker_no24oka', 'speaker_ocise', 'speaker_off2class', 'speaker_olivergierke', 'speaker_opelab', 'speaker_other', 'speaker_palkan', 'speaker_paperswelove', 'speaker_pauldix', 'speaker_pichuang', 'speaker_pixely', 'speaker_prof18', 'speaker_publicservicelab', 'speaker_pyama86', 'speaker_pycon2015', 'speaker_pycon2016', 'speaker_quasilyte', 'speaker_rachelhch', 'speaker_ramalho', 'speaker_redhatlivestreaming', 'speaker_reverentgeek', 'speaker_rmcelreath', 'speaker_rnakamuramartiny', 'speaker_rtechkouhou', 'speaker_sansanbuildersbox', 'speaker_senryakuka', 'speaker_shah', 'speaker_shlominoach', 'speaker_soudai', 'speaker_tagtag', 'speaker_takaking22', 'speaker_takashitanaka', 'speaker_tammielis', 'speaker_tenforward', 'speaker_thockin', 'speaker_thomasvitale', 'speaker_toshiseisaku', 'speaker_tosseto', 'speaker_uzulla', 'speaker_welcometomusic', 'speaker_wescale', 'speaker_yasuoyasuo', 'speaker_ymatsuwitter', 'speaker_yohhatu', 'speaker_yoshiakiyamasaki', 'speaker_ytaka23', 'speaker_ythecombinator', 'speaker_yuyumoyuyu', 'speaker_zoomquiet'],
            label="Author's name", value = "speaker_other"
        )
        author.change(lambda file_info: pop_up4(), inputs=[author], outputs=[])
        prediction_days = gr.Slider(minimum=0, maximum=10000, label="Select the number of days after upload by which the number of views should be forecasted", value=30, visible = False)
        levelofEducation = gr.Dropdown(choices=['High School', 'Undergraduate', 'Graduate', 'PhD'], label="Level of Education of the Audience", value="Undergraduate") 

    with gr.Row():    
        process_btn = gr.Button("⚡ Process the whole Slide Deck (powered by Specialized AI Models) ⚡")
        process_btn.click(lambda file_info: pop_up7(), inputs=[process_btn], outputs=[])

        category.change(lambda file_info: pop_up3(), inputs=[category], outputs=[])
        prediction_days.change(lambda file_info: pop_up5(), inputs=[prediction_days], outputs=[])
        levelofEducation.change(lambda file_info: pop_up6(), inputs=[levelofEducation], outputs=[])
 

    
    with gr.Row():
        fact_display = gr.Markdown(label="Fact Checker Results:")
        #fact_display.change(lambda file_info: pop_up8(), inputs=[fact_display], outputs=[])

    
    with gr.Accordion(label="Decoding the Measurements: How Are Quality Dimensions Assessed?", open=False):
        gr.Markdown("""## Intrinsic Quality
Intrinsic quality refers to the **inherent value of content**, assessed through its **organization, clarity, and relevance**. It is measured quantitatively by analyzing **word frequency entropy** scaled by text length, diversity, and the content itself.
## Contextual Quality
Contextual quality assesses how **informative and relevant** content is, considering factors like the **number of pages**, **image density**, **variability in image use**, and **content category** within a slide deck.
## Representational Quality
Representational quality intricately gauges the **clarity and informativeness** of content by analyzing the **mean word count per slide**, the **standard deviation of word counts** across slides to assess uniformity, and the **aggregate word volume** within the slide deck, offering a understanding of information presentation and density.
## Reputational Quality
Reputational quality evaluates the **authority and trustworthiness** of content by examining the **expertise, recognition, and credibility** of the author and speaker, accounting for their contributions and standing within their field.
""")
    # Output sliders for displaying analysis results.
    quality_dimensions_output = gr.HTML()
    predicted_views_output = gr.HTML()
    


with gr.Blocks() as demo_tab2:
    with gr.Row():    
        image_slider = gr.Gallery(label="Slide Viewer", allow_preview=True, interactive=False)

        async def handle_upload(pdf_file):
                #asyncio.create_task(upload_to_cloud(pdf_file))
            images = process_pdf_to_images(pdf_file)
            return images
        
        #async def upload_to_cloud(pdf_file):
        #    fs = dropboxdrivefs.DropboxDriveFileSystem(token=os.getenv("Dropbox"))
        #    #get date as 4 digit number
        #    timestamp = int(time.time())
        #    print(pdf_file)
        #    fs.put_file(pdf_file, "/slides" + str(timestamp) + ".pdf")
        
        upload.change(handle_upload, inputs=[upload], outputs=[image_slider])  
        category.change(lambda file_info: pop_up3(), inputs=[category], outputs=[])
        prediction_days.change(lambda file_info: pop_up5(), inputs=[prediction_days], outputs=[])
        levelofEducation.change(lambda file_info: pop_up6(), inputs=[levelofEducation], outputs=[])
    
    # Correctly setting up the click event
    process_btn.click(
        asyncprocessing,  # Directly passing the function without naming it 'function'
        inputs=[upload, category, prediction_days, author], 
        outputs=[quality_dimensions_output, predicted_views_output, fact_display]
    )

        

    with gr.Column():
        with gr.Row():
            feedback_button = gr.Button("⚡Give me Feedback on this Slide⚡")
            selected = gr.Number(show_label=False, visible=False)  


    with gr.Accordion(label="Decoding the Feedback: How Are Checkpoints Assessed?", open=False):
        gr.Markdown("""We are able to multimodal analyze your slide design based on 10 checkpoints:
## 1. Insert a pictogram.
Pictogram insertion can intuitively convey the slide content.
## 2. Add a subheading.
Subheading addition makes the audiences convenient to find information.
## 3. Emphasize words.
Emphasizing important words enhances a part of a text to make it noticeable.
## 4. Emphasize areas.
Emphasizing important areas of the slides helps focus attention.
## 5. Add T1 and T2.
Slide title (T1) and slide messages (T2) help the audiences more easily understand the main content of the exposition.
## 6. Use the grid structure.
A grid structure helps organize target and comparison items in rows and columns, creating a table-like format.
## 7. Itemize the text.
Text itemization is good in terms of readability and organization.
## 8. Add a comment.
Comments aid in audiences’ understanding.
## 9. Correct flow.
Left-to-right top-to-bottom flow mimics human scanning methods.
## 10. MECE.
Mutually exclusive and collectively exhaustive (MECE) objects should be aligned without omissions and duplication to make the slides convincing.
""")

    with gr.Row():
        feedback_output = gr.Textbox(label="Slide Feedback")

        
    images = gr.State()  # To store the selected image base64 string
    

    def get_select_index(evt: gr.SelectData):
        return evt.index
    
    image_slider.select(get_select_index, None, selected)
    

    def on_feedback_button_click(images, index):
        index = int(index)
    # Assuming images[index][0] gives the path to the image file
        selected_image_path = images[index][0]  # Adjust based on your actual data structure
        return feedback_generator.process(selected_image=selected_image_path)
    
    feedback_button.click(on_feedback_button_click, inputs=[image_slider, selected], outputs=[feedback_output])

    
demo = gr.TabbedInterface([demo_tab1, demo_tab2], ["Overall Slide Evaluation", "Single Slide Feedback"])

if __name__ == "__main__":
    #demo.queue(default_concurrency_limit = 3)
    demo.launch()
#auth=("Test", os.getenv("accessPassword"))