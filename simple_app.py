import streamlit as st

st.title('Test App')
st.write('If you can see this, the app is working!')

if st.button('Click me'):
    st.balloons()
    st.success('It works!')
