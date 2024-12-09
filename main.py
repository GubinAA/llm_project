from llm import generate_response
import streamlit as st


# Streamlit Frontend

def main():
    st.title("Telegram News AI Assistant")

    query = st.text_input("Enter your query:")
    if query:
        with st.spinner("Generating response..."):
            response, context = generate_response(query)
            st.subheader("Response:")
            st.write(response.content)


# Run Streamlit app
if __name__ == '__main__':
    main()
