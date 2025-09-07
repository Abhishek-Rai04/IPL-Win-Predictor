import streamlit as st

# Minimal Streamlit app
st.set_page_config(page_title="Minimal Test")
st.write("# Streamlit Test Page")
st.write("If you can see this, Streamlit is working!")

# Add a simple button
if st.button("Click me!"):
    st.balloons()
    st.success("It works!")
