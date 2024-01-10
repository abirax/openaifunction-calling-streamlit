# First
import os
import re
from openai import OpenAI
import json


import streamlit as st

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API

OPENAI_API_KEY = ""
openai_api_key=OPENAI_API_KEY
client =OpenAI(api_key=OPENAI_API_KEY)
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})
def enroll_paperless(email):
    """Set the email for paperless billing"""
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat,email):
        return json.dumps({"email": email})
    else:
        return json.dumps({"email": "Invalid Email"})
        
# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#     "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#     "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#     "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot") 
if "messages" not in st.session_state:
    st.session_state["messages"]=[{"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."}]
    st.session_state.messages.append({"role": "assistant", "content": "How can I help you?"})

for msg in st.session_state.messages:
    if isinstance(msg, dict):
        if ('ChatCompletion' in msg):
            continue
        if (msg["role"] == "system" or msg["role"] == "tool"):
            continue
        st.chat_message(msg["role"]).write(msg["content"])
    else:
        # Handle the case when msg is not a dictionary
        pass
os.environ['REQUESTS_CA_BUNDLE'] = 'C:\Abir\Zscaler_Root_CA.crt'
if prompt := st.chat_input():
    # if not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.")
    #     st.stop()
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
            {
            "type": "function",
            "function": {
                "name": "enroll_paperless",
                "description": "Enroll for paperless billing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The email where you want to receive your bills",
                        },
                        
                    },
                    "required": ["email"],
                },
            }
            },
        
    ]

    # Step 1: send the user's prompt and the conversation history to the model
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106", messages=st.session_state.messages, tools=tools)
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo-1106",
    #     messages=messages,
    #     tools=tools,
    #     tool_choice="auto",  # auto is default, but we'll be explicit
    # )
    msg = response.choices[0].message
    tool_calls = msg.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        print(tool_calls)
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "enroll_paperless": enroll_paperless,
        }  # only one function in this example, but you can have multiple
        # extend conversation with assistant's reply
        st.session_state.messages.append(msg)
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            print(tool_call)
            print('----')
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if(function_name=='enroll_paperless'):
                function_response = function_to_call(
                email=function_args.get("email")
            )
            else:    
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
            st.session_state.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106", messages=st.session_state.messages, tools=tools)
        msg=response.choices[0].message
        st.session_state.messages.append(
            {"role": "assistant", "content": msg.content})
        st.chat_message("assistant").write(msg.content)
    else:
        st.session_state.messages.append({"role": "assistant", "content": msg.content})
        st.chat_message("assistant").write(msg.content)
