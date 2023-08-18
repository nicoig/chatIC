# Para crear el requirements.txt ejecutamos 
# pipreqs --encoding=utf8 --force

# Primera Carga a Github
# git init
# git add .
# git commit -m "primer commit"
# git remote add origin https://github.com/nicoig/chatIC.git
# git push -u origin master

# Actualizar Repo de Github
# git add .
# git commit -m "Se actualizan las variables de entorno"
# git push origin master

# Para eliminar un repo cargado
# git remote remove origin

# En Render
# agregar en variables de entorno
# PYTHON_VERSION = 3.9.12

# Pasando a master
# git checkout -b master
# git push origin master



###############################################################



import os
import pickle
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.prompts.prompt import PromptTemplate


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def get_pdf_text(filepaths):
    text = ""
    for filepath in filepaths:
        with open(filepath, "rb") as file:
            pdf = PdfReader(file)
            for page in pdf.pages:
                text += page.extract_text()
    return text

def get_text_chunks(text, chunks_file):
    if os.path.exists(chunks_file):
        with open(chunks_file, 'rb') as f:
            chunks = pickle.load(f)
    else:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        with open(chunks_file, 'wb') as f:
            pickle.dump(chunks, f)
    return chunks

def get_vectorstore(text_chunks, vectorstore_file):
    if os.path.exists(vectorstore_file):
        with open(vectorstore_file, 'rb') as f:
            vectorstore = pickle.load(f)
    else:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        with open(vectorstore_file, 'wb') as f:
            pickle.dump(vectorstore, f)
    return vectorstore

def get_conversation_chain(vectorstore, model_name):
    llm = ChatOpenAI(model_name=model_name)
    qa_template = """
        Eres Mr. Intelicom, el asistente virtual de la área de Inteligencia Comercial de Carozzi. Estás aquí para ayudar y responder las preguntas de los trabajadores de Carozzi de manera amable y eficiente. Si no conoces una respuesta, simplemente indica que no la sabes en lugar de intentar adivinarla. Si una pregunta no está relacionada con las áreas de tu competencia, cortésmente señala que estás aquí para ayudar en temas relacionados con la Inteligencia Comercial de Carozzi. Utiliza los fragmentos de contexto a continuación para formular tu respuesta.

        context: {context}
        =========
        question: {question}
        ======
    """

    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context","question" ])
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={'prompt': QA_PROMPT}
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
            

def main():
    load_dotenv()
    st.set_page_config(page_title="Chat Mr. Intelicom", page_icon=":books:", layout="wide")
    st.write(css, unsafe_allow_html=True)

    st.sidebar.title('Menu')
    model_name = st.sidebar.selectbox(
        'Selecciona un modelo de LLM:',
        ('gpt-3.5-turbo', 'gpt-3.5-turbo-16k','text-davinci-003','gpt-4') # Puedes poner los modelos que quieras aquí
    )
    temperature = st.sidebar.slider('Ajusta la temperatura:', min_value=0.0, max_value=1.0, value=0.1, step=0.1)

    if "initialized" not in st.session_state:
        file_directory = 'files'
        filepaths = [os.path.join(file_directory, file) for file in os.listdir(file_directory) if file.endswith('.pdf')]
        text = get_pdf_text(filepaths)

        chunks_file = 'chunks.pkl'
        chunks = get_text_chunks(text, chunks_file)

        vectorstore_file = 'vectorstore.pkl'
        vectorstore = get_vectorstore(chunks, vectorstore_file)

        st.session_state.conversation = get_conversation_chain(vectorstore, model_name)
        st.session_state.llm_temperature = temperature
        st.session_state.chat_history = []
        st.session_state.initialized = True


    # Mostrar la imagen
    st.image('img/logo_white.png', width=300)

    # Estableciendo el título
    st.header("🍅🌾 Chat con Mr. Intelicom 🌾🍅")

    # Estableciendo el subtítulo
    #st.subheader("Chatea, explora y aprende de forma dinámica")


    st.write("""
    Soy Mr. Intelicom, el asistente virtual del área de Inteligencia Comercial de Carozzi. Estoy aquí para ayudarte a entender y resolver dudas acerca de los reportes y métricas relevantes para los trabajadores de Carozzi. A través de este chatbot, puedes consultar sobre:

    - Los diferentes reportes disponibles clasificados por Cargo y Grupo.
    - El contenido específico de cada reporte y los datos que proporcionan.
    - Fórmulas relevantes utilizadas en cada reporte para obtener métricas e indicadores clave.
    - Cualquier otra duda o consulta relacionada con la Inteligencia Comercial de Carozzi.
""")


    user_question = st.text_input("Realiza tu consulta:")
    if st.button('Enviar'):  
        if user_question:
            handle_userinput(user_question)


if __name__ == '__main__':
    main()
