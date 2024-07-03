## Creative Best Practice App

import streamlit as st
from PIL import Image
import google.generativeai as genai
from time import sleep
import typing_extensions as typing
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
import io
import os

#GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_API_KEY = "AIzaSyAGDmfLr3UGl1zV3uRHhysa4aCoaYsoXcA"
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

def get_screenshot_from_url(url):
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    browser = webdriver.Firefox(
        options=options,
        )

    browser.get(url)
    sleep(2)

    width = browser.execute_script('return document.body.parentNode.scrollWidth')
    height = browser.execute_script('return document.body.parentNode.scrollHeight')
    browser.set_window_size(width, height)

    body = browser.find_elements(By.TAG_NAME, "body")
    temp = io.BytesIO(body[0].screenshot_as_png)
    
    image = Image.open(temp)
    browser.quit()

    return image

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
_ = installff()
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
                screenshot = Image.new('RGB', (10, 10))
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
                    
                    if screenshot or screenshot is not None or screenshot != "":
                        st.image(screenshot, use_column_width=True)
                
            
                with col2:
                    #Show Gemini response on second column of the main page
                    st.header("Does the ASO Page meet best practices?")
                    st.divider()
                    with st.container(height=700,border=False):
                        st.markdown(response)

            #with row0_col2:
            #    show_download_pdf_button("Download PDF","creative_best_practice.pdf",download_pdf_ad_creatives_responses)
