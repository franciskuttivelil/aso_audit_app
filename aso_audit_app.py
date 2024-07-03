## Creative Best Practice App

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from time import sleep
import time
import typing_extensions as typing
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import tempfile
from fpdf import FPDF
import cv2
import streamlit.components.v1 as components
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import io

#GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_API_KEY = "AIzaSyAGDmfLr3UGl1zV3uRHhysa4aCoaYsoXcA"
genai.configure(api_key=GEMINI_API_KEY)

def get_screenshot_from_url(url):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    temp = io.BytesIO(browser.get_screenshot_as_png())
 
    image = Image.open(temp)
    browser.quit()

    return image

def get_thumbnail_from_video(uploaded_video_file):
    frame_number = 5
    video_file_path = create_path_for_uploaded_file(uploaded_video_file)
    cap = cv2.VideoCapture(video_file_path)
    amount_of_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if amount_of_frames > 5:
        frame_number = 5
    else:
        frame_number = 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
    res, frame = cap.read()

    return Image.fromarray(frame)

class PDF(FPDF):

    def footer(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))
        self.set_y(-15)
        self.set_font('Roboto', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')
        self.image(os.path.join(__location__,'Small MCSP vertical logo.png'),0.9*210,0.9*297,10,20)

def create_letterhead(pdf, WIDTH, HEIGHT):
    __location__ = os.path.realpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))
    pdf.image(os.path.join(__location__,'MCSP Black_Horizontal-01.png'), 0.25*WIDTH, 0.10*HEIGHT, 100, 50)

def create_title(title, pdf, WIDTH,HEIGHT):
    
    # Add main title
    pdf.set_font('Roboto', 'b', 20)  
    pdf.set_xy(0.25*WIDTH,0.50*HEIGHT)
    pdf.cell(100,50,txt=title, align="C")
    pdf.ln(10)
    # Add date of report
    pdf.set_font('Roboto', '', 14)
    pdf.set_x(0.25*WIDTH)
    pdf.cell(100,50,txt=f'{time.strftime("%d/%m/%Y")}', align="C")
    pdf.ln(10)

    #Add contact info
    pdf.set_font('Roboto', '', 14)
    pdf.set_x(0.25*WIDTH)
    pdf.cell(100,50,txt='Email : dane.buchanan@mcsaatchiperformance.com', align="C")
    pdf.ln(10)

def write_to_pdf(download_pdf_ad_creatives_responses):
    
    TITLE = "Ad Creative Best Practices Report"
    WIDTH = 210
    HEIGHT = 297

    __location__ = os.path.realpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))
    # Create PDF
    pdf = PDF() # A4 (210 by 297 mm)
    pdf.add_font("Roboto", style="", fname=os.path.join(__location__, 'Roboto-Regular.ttf'))
    pdf.add_font("Roboto", style="B", fname=os.path.join(__location__, 'Roboto-Bold.ttf'))
    pdf.add_font("Roboto", style="I", fname=os.path.join(__location__, 'Roboto-Italic.ttf'))
    pdf.add_font("Roboto", style="BI", fname=os.path.join(__location__, 'Roboto-BoldItalic.ttf'))

    #First Page of PDF

    # Add Page
    pdf.add_page()

    # Add lettterhead and title
    create_letterhead(pdf, WIDTH, HEIGHT)
    create_title(TITLE, pdf, WIDTH, HEIGHT)
    
    for download_pdf_ad_creatives_response in download_pdf_ad_creatives_responses:

        uploaded_file = download_pdf_ad_creatives_response["uploaded_file"]
        words = download_pdf_ad_creatives_response["response"]
        # Set text colour, font size, and font type
        pdf.set_font('Roboto', 'b', 16)
        pdf.set_margins(10,10)
        pdf.add_page()
        pdf.multi_cell(0.30*WIDTH,txt="Ad Creative", align="C")
        pdf.set_xy(0.39*WIDTH,10)
        pdf.multi_cell(0,txt="Does the Ad Creative meet best practices?", align="C")
        pdf.set_xy(10,20)
        pdf.line(10,20,0.35*WIDTH,20)

        if uploaded_file is not None:
                uploaded_file_type = ((uploaded_file.type).split("/"))[0]
                if uploaded_file_type == "image":
                    image = Image.open(uploaded_file)
                if uploaded_file_type == "video":
                    image = get_thumbnail_from_video(uploaded_file)

        pdf.set_xy(10,30)
        pdf.image(image, w=0.30*WIDTH)
        pdf.set_xy(0.40*WIDTH,20)
        pdf.line(0.40*WIDTH,20,0.95*WIDTH,20)
        pdf.set_xy(0.40*WIDTH,30)
        pdf.set_font('Roboto', '', 12)
        pdf.multi_cell(0,txt=words,markdown=True,align="J")

    return bytes(pdf.output())

#Create temporary file out of uploaded file so that it can be uploaded to Gemini
def create_path_for_uploaded_file(uploaded_file):
    byte_stream = uploaded_file

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    # Write the content of the BytesIO object to the temporary file
        temp_file.write(byte_stream.getvalue())
        temp_file_path = temp_file.name

    return temp_file_path

@st.experimental_fragment
def show_download_pdf_button(label,file_name,download_pdf_ad_creatives_responses):
    st.download_button(
        label=label,
        data=write_to_pdf(download_pdf_ad_creatives_responses),
        file_name=file_name,
        mime="application/octet-stream",
        type="primary",
        use_container_width=True
        )

def upload_to_gemini(path, mime_type=None):
  #Uploads the given file to Gemini.
  #See https://ai.google.dev/gemini-api/docs/prompting_with_media
 
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

#Delete file uploaded to Gemini
def delete_ad_creative_file_from_gemini(ad_creative_file):
    genai.delete_file(ad_creative_file.name)
    print(f'Deleted {ad_creative_file.display_name}.')

def wait_for_files_active(files):
  #Waits for the given files to be active.

  #Some files uploaded to the Gemini API need to be processed before they can be
  #used as prompt inputs. The status can be seen by querying the file's "state"
  #field.

  #This implementation uses a simple blocking polling loop. Production code
  #should probably employ a more sophisticated approach.
  
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

## Function to load Gemini model and get respones
def get_gemini_response(input):
    generation_config = {
                         "temperature": 1,
                         "top_p": 0.95,
                         "top_k": 64,
                         "response_mime_type": "text/plain"
                         }
    model = genai.GenerativeModel(model_name = 'gemini-1.5-pro',
                                  generation_config=generation_config)

    safety_settings = {HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                       HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                       HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                       HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                       }
    response = model.generate_content([input],
                                      safety_settings=safety_settings
                                      )
    return response.text
    
##initialize our streamlit app
st.set_page_config(page_title="ASO Audit App", layout = "wide")
st.html(
"""
<style>
[data-testid="stSidebarContent"] {
    color: white;
    background-color: blue;
}
[data-testid="stFileDropzoneInstructions"] {
    content: "xxxxxx";
}
[data-testid="stWidgetLabel"] {
    color: white;
    background-color: blue;
}
</style>
"""
)

##create the sidebar
with st.sidebar:
    st.image("https://www.mcsaatchiperformance.com/wp-content/themes/mandcsaatchiperformance/assets/img/logo-upright.png", width=230)
    with st.form("inputs", border=False):
        #st.divider()
        st.write("")
        url = st.text_input("Enter URL of App Store Page")
        submit=st.form_submit_button("Analyse App Store Page",type="primary",use_container_width=True)


##create the main page
placeholder = st.empty()
sleep(0.5)
with placeholder.container():
    st.title("ASO Audit App")
    st.divider()
    st.header("What does this app do?")
    st.write("This app helps analyse if an app store page meets best practices. It provides the app store page's strengths, what can be improved\
          and how the app store page can be optimised.")
    st.header("How to use this app?")
    st.write("In the sidebar to the left, paste the app store page url and\
          press 'Analyse App Store Page'. The app will generate insights on your app store page and then provide recommendations")
    st.header("Contact us")
    st.write("Send an email to dane.buchanan@mcsaatchiperformance.com if you have any queries or are facing any issues.")
    
    st.write("")
    st.write(":red[*This app aids in idea generation. Since, recommendations may not always be 100% accurate,\
              please use your judgment before implementing them.]")

## Define behaviour when Analyse button is clicked
if submit:
    if url is None or url == "" or not url:
        placeholder.empty()
        sleep(0.5)
        placeholder.error("Please upload an Ad Creative to analyse using the 'Browse files' button in the sidebar on the left")
    
    else:
        input_prompt = """
               I am an appstore optimisation specialist. I want to make sure that the app store page of our client app is meeting best practices. 
               Please analyse the app store page to see if it meets best practices to make sure it can rank high is appstore rankings and generate optimal organic installs.
               Please include in the response the app store page's strengths, areas to improve and recommendations.
               he app url is {}.
               """.format(url)
        placeholder.empty()
        sleep(0.5)
        with placeholder.container():
            row1 = st.container()

            with row1:
                with st.spinner('Analysing ASO Page ...'):
                    response = ""
                    try:
                        #Get Response from Gemini
                        response=get_gemini_response(input_prompt)
                        #Get screenshot
                        screenshot =get_screenshot_from_url(url)
                        
                    except Exception as e: 
                        print(e)


                col1, col2= st.columns([0.3,0.7], gap="large")

                with col1:
                    #Show ad creative on first column of the main page
                    st.header("ASO Page")
                    st.divider()
                    
                    st.image(screenshot, use_column_width=True)
                
            
                with col2:
                    #Show Gemini response on second column of the main page
                    st.header("Does the ASO Page meet best practices?")
                    st.divider()
                    with st.container(height=700,border=False):
                        st.markdown(response)

            #with row0_col2:
            #    show_download_pdf_button("Download PDF","creative_best_practice.pdf",download_pdf_ad_creatives_responses)