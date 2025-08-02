import streamlit as st

# Set page title
st.set_page_config(page_title="Hello App")

# Display content
st.title("👋 Hello, World!")
st.write("This is a basic Streamlit app running inside Choreo Web App.")

# Interactive element
name = st.text_input("What's your name?")
if name:
    st.success(f"Nice to meet you, {name}!")
