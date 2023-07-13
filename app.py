from flask import Flask, jsonify, request
from io import BytesIO
from langchain import OpenAI, LLMChain, PromptTemplate
from dotenv import load_dotenv
import os
from github import Github, Auth
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

class Upload:
    def __init__(self):
        self.file = None 
        self.fileName = ""
        self.fileContent = ""
        self.githubURL = ""
        self.accessToken =""
        self.option = -1
        self.code=""

    def code_from_file(self):
        self.code = self.fileContent
    
    def code_from_github(self):
        print("in function")
        url = self.githubURL
        accessToken = self.accessToken
        myGit = Github(accessToken)
        print(myGit.get_user().login)
        _, _, _, owner, repo, _,_,file = url.split('/', 7)
        print(f"{owner}/{repo}")
        repo = myGit.get_repo(f"{owner}/{repo}")
        contents = repo.get_contents(file)
        self.code = contents.decoded_content
        print(self.code)
    
    def response_from_openAI(self):
        print("in OpenAI function")
        template=""
        if self.option == '1':
            template ="""List your security review and improvements in bullet points for the following code: {code_content}"""
        elif self.option == '2':
            template ="""Provide documentation for the following code: {code_content}"""
        elif self.option == '3':
            template ="""List the errors and improvements for the following code: {code_content}"""
        else:
            template ="""Provide feedback for the following code: {code_content}"""
        reviewPrompt = PromptTemplate(input_variables=["code_content"], template=template)
        load_dotenv()
        openai.api_key = os.environ["OPENAI_API_KEY"]
        llm = OpenAI(temperature=0.0)
        reviewChain = LLMChain(llm =llm, prompt = reviewPrompt)
        response = reviewChain.predict(code_content = self.code)
        print(response)
        return response

echo = Upload()



@app.route("/url_route", methods=['POST'])
def upload_file():

    uploadStatus = {}
    try:
        echo.file = request.files['file_from_react']
        echo.fileName = echo.file.filename
        print(f"Uploading file {echo.fileName}")
        file_bytes = echo.file.read()
        echo.fileContent = BytesIO(file_bytes).readlines()
        print(echo.fileContent)

        echo.code_from_file()
        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload file {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)

@app.route("/upload_text_url_route", methods=['POST'])
def upload_githubURL():

    uploadStatus = {}
    try:
        print("Trying to upload url")
        echo.githubURL = request.json["url"]
        echo.accessToken = request.json["accessToken"]
        echo.code_from_github()
        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload url {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)

@app.route("/choose_service", methods=['POST'])
def service_choice():

    uploadStatus = {}
    try:
        echo.option = request.json['option']
        print(echo.option)
        uploadStatus['status'] = 1

    except Exception as e:
        print(f"Couldn't upload url {e}")
        uploadStatus['status'] = 0

    return jsonify(uploadStatus)

@app.route("/run_echo", methods=['GET'])
def run_echo():
    response = echo.response_from_openAI()
    return jsonify({'response' : response})

# if __name__ == '__main__': 
   # app.run()
