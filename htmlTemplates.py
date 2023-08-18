css = '''
<style>
body {
    background-color: #000000;  /* Color de fondo para todo el cuerpo de la página */
    color: #ffffff;  /* Color de texto general para todo el cuerpo de la página */
}
.reportview-container {
    max-width: 60%;
    margin: auto;
    background-color: #262626;  /* Cambia el color de fondo del contenedor de la aplicación Streamlit */
    color: #ffffff;  /* Cambia el color de texto del contenedor de la aplicación Streamlit */
    padding: 10px;  /* Agrega algo de espacio alrededor del contenedor de la aplicación Streamlit */
}
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 50%;
  padding: 0 1.5rem;
  color: #fff;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="data:image/png;base64,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" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://cdn-icons-png.flaticon.com/512/186/186313.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
