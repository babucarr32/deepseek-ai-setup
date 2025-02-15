import asyncio
from ollama import chat, generate, AsyncClient

import streamlit as st
import json

user = {}
assistant = {}
ai_system = {}
CHAT_LIST_FILE_NAME = 'chat-list.json'
    
def handle_set_new_chat():
    ai_system['role'] = 'system'
    ai_system['content'] = 'New chat'

def get_all_chats():
    chats = read_file(CHAT_LIST_FILE_NAME)
    return chats

def handle_new_chat(fileName: str):
    handle_set_new_chat() 
    st.session_state['chatIndex'] = fileName 

def handle_chats(question: str, answer: str):
    user['role'] = 'user'
    user['content'] = question

    assistant['role'] = 'assistant'
    assistant['content'] = answer

def read_file(file_name: str) -> [str]:
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

if not 'allChats' in st.session_state:
    st.session_state['allChats'] = get_all_chats()

def save_file(file_name: str):
    content = read_file(file_name)

    if not len(content):
        handle_set_new_chat()
        content.append(ai_system)
        handle_save_chat_title_and_index(user['content'], file_name)
        
    content.append(user)
    content.append(assistant)

    with open(file_name, 'w+', encoding='utf-8') as f:
        json.dump(content, f)
    f.close()
    st.session_state['allChats'] = get_all_chats()

def handle_save_chat_title_and_index(title: str, file_name: str):
    chats = read_file(CHAT_LIST_FILE_NAME)
    new_chat = { 'title': title, 'fileName': file_name }
    chats.insert(0, new_chat)
    
    with open(CHAT_LIST_FILE_NAME, 'w+', encoding='utf-8') as f:
        json.dump(chats, f)

def display_previous_prompts(messages):
    content = read_file(st.session_state['chatIndex'])
    if (content):
        for c in content:
            role = c['role']
            if (role == 'user'):
                prompt = c['content']
                messages.chat_message("user").write(prompt)
            else:
                answer = c['content']
                messages.chat_message("assistant").write(answer)

async def generate_title_based_on_conversiont(prompt):
    'Considering implementation'
    # Todo

if 'chatIndex' not in st.session_state:
    all_chats = get_all_chats()
    chat_length = len(all_chats)
    if chat_length:
        st.session_state['chatIndex'] = f'chat{chat_length}.json'
    else:
        st.session_state['chatIndex'] = 'chat0.json'

# Using "with" notation
with st.sidebar:
    all_chats = st.session_state['allChats']
    chat_length = len(all_chats)
    
    if st.button('Add new', type='primary', use_container_width=True):
        handle_new_chat(f'chat{chat_length + 1}.json')

    
    for c in all_chats:
        title = c['title']
        fileName = c['fileName']

        if len(title) > 30:
            title = title[:30] + '...'
        if st.button(title, key=title, use_container_width=True):
            handle_new_chat(fileName)

prompt = st.chat_input("Say something")
prevMsg = ''

content = read_file(st.session_state['chatIndex'])

if not len(content):
    handle_set_new_chat()
    content.append(ai_system)
    
if prompt:
  stream = chat(
      model='deepseek-r1:8b',
      messages= content + [{'role': 'user', 'content': prompt}],
      stream=True)

  def stream_data():
    global prevMsg
    for chunk in stream:
      content = chunk['message']['content']
      st.session_state['reply'] = prevMsg + content
      prevMsg = st.session_state['reply'] 
      yield content

  messages = st.container()
  display_previous_prompts(messages)
  messages.chat_message("user").write(prompt)
  messages.chat_message("assistant").write(stream_data())
  handle_chats(prompt, prevMsg)
  save_file(st.session_state['chatIndex'])

else:
    messages = st.container()
    display_previous_prompts(messages)
    
      
