from bs4 import BeautifulSoup
from google import genai
from google.genai.types import GenerateContentConfig
import requests
from urllib.parse import urljoin
import os
import gradio as gr

# pip freeze > requirements.txt
url = r"https://kidobotics.com/index.html"
response = requests.get(url)
soup = BeautifulSoup(response.content,'html.parser')
links = soup.find_all('a')
new_response=[]

for link in links:
    if link.get('href').startswith("https"):
        new_response.append(link.get('href'))
        
    else :
        new_response.append(urljoin(url,link.get('href')))
    
all_content = ""
for link in new_response:
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        all_content += soup.body.get_text(strip=True,separator="\n")
    except requests.RequestException as e:
        print(e)
        
print(all_content)

GEMINI_API_KEY=os.environ.get('GOOGLE_SECRET_KEY')
MODEL3="gemini-2.0-flash"
client = genai.Client(api_key=GEMINI_API_KEY)

content = " you are an agent i am providing you some data or i can say some \
        knowledge about a website if someone says hi then gives the intrduction of the service\
        provided by that website and further you can proceed according to user will ask \
        anything but if ask something related to website only then answer him and \
        firstly research deeply from your side if you find answer then give that \
        otherwise say some managable thing and promote the website' "
content += all_content

def chat(message,history):
    print(f"message message == {message}\n\n")
    print(f"history history == {history}\n\n")
    response = client.models.generate_content(
        model=MODEL3,contents=message,
        config=GenerateContentConfig(
            system_instruction=[
                content
            ]
        ),
    )
    new_res=""
    for res in response.text:
        new_res+= res
        yield new_res

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", 7860)))
    gr.ChatInterface(fn=chat).launch(
        server_name="0.0.0.0",  
        server_port=port,
        share=False            
    )
