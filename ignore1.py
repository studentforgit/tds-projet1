from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "script_runner",
            "description": "Install a package and run a script from a url with provided arguments",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_url": {
                        "type": "string",
                        "description": "The url of the script to run",
                    },
                    "args": {
                        "type": "array",
                        "description": "List of arguments to pass to the script",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": ["script_url", "args"],
            },
        },
    },
]

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/read")
def read_file(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found")

@app.post("/run")
def task_runner(task: str):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": task},
            {"role": "system", "content": """
                You are an assistant who has to do a variety of tasks. 
                If your task involves running a script, you can use the script_runner tool.
                If your task involves writing a code, you can use the task_runner tool.
                
                Supported Tasks:
                - A2: Read a file's contents.
                - A3: Write content to a file.
                - A4: List files in a directory.
                - A5: Execute a shell command.
                - A6: Fetch JSON from a URL.
                - A7: Parse JSON content.
                - A8: Search for a pattern in a text file.
                - A9: Summarize text content.
                - A10: Extract data from structured text.
            """}
        ],
        "tools": tools,
        "tool_choice": "auto"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.post("/write")
def write_file(path: str, content: str):
    try:
        with open(path, "w") as f:
            f.write(content)
        return {"message": "File written successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

@app.get("/list")
def list_files(directory: str = "."):
    try:
        return {"files": os.listdir(directory)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.post("/execute")
def execute_command(command: str):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import requests
# import os
# import json
# import subprocess

# app = FastAPI()
# AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["GET", "POST"],
#     allow_headers=["*"],
# )
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "script_runner",
#             "description": "Install a package and run a script from a url with provided arguments",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "script_url": {
#                         "type": "string",
#                         "description": "The url of the script to run",
#                     },
#                     "args": {
#                         "type": "array",
#                         "description": "List of arguments to pass to the script",
#                         "items": {
#                             "type": "string",
#                         },
#                     },
#                 },
#                 "required": ["script_url", "args"],
#             },
#         },
#     },
# ]
# def query_gpt(task):
#     url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {AIPROXY_TOKEN}"
#     }
#     json = {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {"role": "user", "content": user_input},
#             {"role": "system", "content": """Whenever you receive a system directory location, always make it to a relative path, 
#              for example adding a . before it would make it relative path, 
#              rest is on you to manage, I just want the relative path
#             """}],
#         "tools": tools,
#         "tool_choice": "auto"
#     }
# AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

# @app.get("/")
# def home():
#     return {"message": "Hello World"}

# @app.get("/read")
# def read_file(path: str):
#     try:
#         with open(path, "r") as f:
#             return f.read()
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=f"File not found")

# @app.post("/run")
# async def run(task: str):
#     query = query_gpt(task)
#     print(query)
#     func = eval(query["choices"][0]["message"]["tool_calls"][0]["function"]["name"])
#     args = json.loads(query["choices"][0]["message"]["tool_calls"][0]["arguments"]) 
#     output = func(**args)
#     return output



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

