
import streamlit as st

# Agent and LLM
from langchain import LLMChain, OpenAI
from langchain.agents import AgentExecutor, Tool, ConversationalAgent
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI
# Memory
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
# Tools
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.utilities import OpenWeatherMapAPIWrapper
from langchain_groq import ChatGroq


import random
import os
import requests
import asyncio

st.title("Bird Watching Assistant")

st.text('''Funcionalitys:

- Ask questions about birds
- Get current weather in a location to know if is possible to birdwatch
- Get a random bird song
- Get a specific bird song''')


# Set Tools
SERPER_API_KEY = os.getenv("SERPER_API_KEY") 
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
weather = OpenWeatherMapAPIWrapper(openweathermap_api_key=OPENWEATHERMAP_API_KEY)


async def random_canto(_):
    url = "https://xeno-canto.org/api/2/recordings?query=cnt:brazil"

    response = requests.get(url)

    json = response.json()

    rand = random.randint(0, len(json['recordings'])-1)

    # consigo o file a partir do ID
    file_url = json['recordings'][rand]['file']
    name_url = json['recordings'][rand]['en']

    # baixo o arquivo
    response = requests.get(file_url, stream=True)

    # salvo o arquivo em um arquivo local
    with open('.\cantos\canto.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
    print("Canto da Ave: "+name_url)
    print("Arquivo baixado com sucesso!")

    st.audio('.\cantos\canto.mp3')

async def pesquisa_canto(nome_ave):
    url = f"https://xeno-canto.org/api/2/recordings?query={nome_ave}"

    response = requests.get(url)

    json = response.json()

    rand = random.randint(0, len(json['recordings'])-1)

    # consigo o file a partir do ID
    file_url = json['recordings'][rand]['file']

    # baixo o arquivo
    response = requests.get(file_url, stream=True)

    # salvo o arquivo em um arquivo local
    with open('.\cantos\canto_especifico.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

    print("Arquivo baixado com sucesso!")

    # toca o arquivo mp3 com streamlit

    #st.subheader("Canto da Ave: "+nome_ave)
    st.audio('.\cantos\canto_especifico.mp3')

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for when you need to get especific information about a topic like a bird curiosity or a atuality. Input should be a search query.",
    ),
    Tool(
        name="Weather",
        func=weather.run,
        description="Useful for when you need to get the current weather in a location.",
    ),
    Tool(
        name="Canto Aleatório",
        func=lambda input: asyncio.run(random_canto(input)),
        description="Useful for when you need to get a random bird song.",
    ),
    Tool(
        name="Canto Específico",
        func=lambda input: asyncio.run(pesquisa_canto(input)),
        description="Useful for when you need to get a specific bird song. Like cockatiel, lovebird, conures, etc.",
    )

]

# Set Chat Conversation

prefix = """ You are a friendly bird watching assistant.
You can help users to listen bird songs based on their preferences.
You have access to the following tools:"
"""

suffix = """
Chat History:
{chat_history}
Latest Question: {input}
{agent_scratchpad}
"""

prompt = ConversationalAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input",
                     "chat_history",
                     "agent_scratchpad"],
)

# Set Memory

msg = StreamlitChatMessageHistory()

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        messages=msg,
        memory_key="chat_history",
        return_messages=True
    )
memory = st.session_state.memory

# Set Agent

llm_chain = LLMChain(
    llm=ChatGroq(temperature=0.8, model_name="llama3-8b-8192"),
    prompt=prompt,
    verbose=True
)

agent = ConversationalAgent(
    llm_chain=llm_chain,
    memory=memory,
    verbose=True,
    max_interactions=3,
    tools=tools,
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                    tools=tools,
                                                    memory=memory,
                                                    verbose=True)

#query = st.text_input("O que você quer fazer hoje?", placeholder="Digite aqui...")
query = st.text_input("What you want to know about birds?")

if query:
    with st.spinner("Estou pensando..."):
        result = agent_executor.run(query)
        st.info(result, icon="🤖")

with st.expander("My thinking"):
    st.write(st.session_state.memory.chat_memory.messages)