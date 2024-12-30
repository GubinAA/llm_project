import streamlit as st
from llm import generate_response

def main():
    st.title("Telegram News AI Assistant")
    st.write("Введите ваш запрос, и ассистент найдёт релевантные новости из Telegram.")

    query = st.text_input("Ваш запрос:")
    top_k = st.slider("Сколько результатов искать?", min_value=1, max_value=5, value=3)

    if st.button("Сформировать ответ"):
        if not query.strip():
            st.warning("Пожалуйста, введите запрос.")
        else:
            with st.spinner("Генерация ответа..."):
                response, context = generate_response(query, top_k=top_k)
                st.subheader("Ответ:")
                st.write(response)
                st.subheader("Использованный контекст и ссылки:")
                for idx, (txt, lnk) in enumerate(context, start=1):
                    st.markdown(f"**Источник {idx}:** {txt[:200]}...")
                    st.markdown(f"[Ссылка на сообщение]({lnk})")

if __name__ == '__main__':
    main()