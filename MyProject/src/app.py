import gradio as gr
from chatbot.chatbot_backend import ChatBot
from utils.ui_settings import UISettings

# Enhanced CSS for Modern UI
css = """
/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: #f3f4f6;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Layout */
.container {
    display: flex;
    flex-direction: row;
    height: 100vh;
    width: 100%;
    overflow: hidden;
    
}

#main-content {
    flex: 1;
}

#sidebar {
    width: 180px; /* Fixed width */
    background-color: #000;
    padding: 14px 10px;
    display: flex;
    flex-direction: column;
    align-items: flex-start; /* Align items to the left */
    justify-content: flex-start; /* Align vertically to the top */
    position: fixed; /* This will make sure sidebar is fixed on the left */
    height: 100vh; /* Make sidebar full-height */
    top: 0;
    left: 0;
}

.app-title {
    font-size: 20px;
    font-weight: 600;
    color: #6b21a8;
    padding: 0 12px;
    margin-bottom: 24px;
}

.nav-btn {
    display: flex !important;
    align-items: center;
    gap: 12px;
    text-align: left;
    padding: 10px 12px;
    border-radius: 8px;
    color: #4b5563;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.2s;
    border: none;
    background: none;
    width: 100%;
    cursor: pointer;
}

.nav-btn:hover {
    background-color: #f3f4f6;
    color: #6b21a8;
}

.nav-btn svg, .nav-btn img {
    width: 20px;
    height: 20px;
    opacity: 0.7;
}

/* Main Content */
#main-content {
    flex: 1;
    margin-left: 180px; /* This will give space to the left side for the sidebar */
    display: flex;
    flex-direction: column;
    padding: 32px;
}

/* Welcome Message */
.welcome-message {
    text-align: center;
}

.welcome-badge {
    background-color: #6b21a8;
    color: white;
    padding: 8px 16px;
    border-radius: 9999px;
}

.welcome-title {
    font-size: 48px; 
}

.welcome-subtitle {
   font-size: 32px; 
   color:#6b21a8; 
}

.welcome-text {
   color:#6b7280; 
   font-size :16px; 
   line-height :1.5; 
}

.feedback textarea {
    background-color: #FFCCCB !important;
}

#chat textarea{
    background-color: #FFCCCB !important;

}

/* Input Container */
.input-container {
   display:flex; 
   align-items:center; 
   gap :8px; 
    background-color: #FFCCCB !important;
    padding: 16px;  /* Optional: Add padding */
    border-radius: 8px;  /* Optional: Add border radius */

}

/* Textbox */
#input-box {
   height :50px !important; 
   padding :4px 8px !important; 
   background-color: #FFCCCB !important;

}

/* Send Button */
#send-btn {
   height :36px !important; 
   width :36px !important; 
}

/* Settings Button Position */
.settings-btn {
   margin-top:auto; 
}
"""

# Launch Gradio App
with gr.Blocks(css=css) as demo:
    
    with gr.Row(elem_classes="container"):
        # Sidebar Navigation
        with gr.Column(elem_id="sidebar"):
            gr.Markdown("AI Data Reporting", elem_classes="app-title")
            gr.Button("📝 New Query", elem_classes="nav-btn")
            gr.Button("🔍 Search", elem_classes="nav-btn")
            gr.Button("🏠 Home", elem_classes="nav-btn")
            gr.Button("⭐ Saved", elem_classes="nav-btn")
            gr.Button("📜 History", elem_classes="nav-btn")
            with gr.Column(elem_classes="settings-btn"):
                gr.Button("⚙️ Settings", elem_classes="nav-btn")

        # Main Content
        with gr.Column(elem_id="main-content"):
            welcome_msg = gr.Markdown(
                """
                <div class="welcome-message">
                    <div class="welcome-badge">Welcome to AI Data Reporting</div>
                    <h1 class="welcome-title">Hi there, User!</h1>
                    <h2 class="welcome-subtitle">What would you like to know?</h2>
                    <p class="welcome-text">Simply ask your question in everyday language and uncover insights instantly, effortlessly!</p>
                </div>
                """,
                visible=True
            )
            
            # chatbot = gr.Chatbot(
            #     [],
            #     elem_classes="feedback",
            #     avatar_images=("images/AI_RT.png", "images/openai.png"),
            #     render=False
            # )
            # chatbot = gr.Chatbot([], elem_id="chatbot")
            chatbot = gr.Chatbot([], label="Watchtower Output").style(color_map=["white","black"])


            # **Adding like/dislike icons
            chatbot.like(UISettings.feedback, None, None)


            with gr.Row():
                input_txt = gr.Textbox(
                    elem_classes="feedback",
                    lines=3,
                    scale=8,
                    placeholder="Enter text and press enter, or upload PDF files",
                    container=False,
                )

            with gr.Row() as row_two:
                text_submit_btn = gr.Button(value="Submit text")
                clear_button = gr.ClearButton([input_txt, chatbot])
            ##############
            # Process:
            ##############
            txt_msg = input_txt.submit(fn=ChatBot.respond,
                                       inputs=[chatbot, input_txt],
                                       outputs=[input_txt, chatbot],
                                       queue=False).then(
                lambda: gr.Textbox(interactive=True,elem_classes="feedback"),
                None, [input_txt], queue=False
            )

            # Handling the button click action
            txt_msg = text_submit_btn.click(fn=ChatBot.respond,
                                            inputs=[chatbot, input_txt],
                                            outputs=[input_txt, chatbot],
                                            queue=False).then(
                lambda: gr.Textbox(interactive=True,elem_classes="feedback"),
                None, [input_txt], queue=False
            )


if __name__ == "__main__":
    demo.launch()

