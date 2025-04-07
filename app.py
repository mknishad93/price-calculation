
import requests
from flask import Flask, jsonify
import streamlit as st
from flask import Flask, jsonify
from deltacalculate.maicall import DeltaValue, CreateToken
import logging

# Flask API Setup

value = DeltaValue()
getToken = CreateToken()

logging.basicConfig(
    level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Streamlit Interface


if st.button("Running Trade"):
    try:
        # Call the Flask API
        value.calling1()

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
                       
st.title("Fill the form to create the token")
with st.form("create_token"):
 name = st.text_input("Enter the username", placeholder="Type user name here...")
 id = st.text_input("Enter the code", placeholder="Type user code here...")
 token = st.text_input("Enter the token",placeholder="Type expiry here...")
 submitted = st.form_submit_button("Submit")

if submitted:    
   if name and id and token:
        logging.info("Entred in method -----")
        msg =getToken.token(name,id,token)
        data = {"message": " {msg} "}
        st.success(f"Hello, {data}")
   else:
       st.error("error")    

if st.button("Get Data from Flask API"):
    try:
        # Call the Flask API
        response = requests.get("http://127.0.0.1:5000/api/data")
        if response.status_code == 200:
            data = response.json()
            st.write("API Response:", data)
        else:
            st.error("Failed to get data from the API.")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")




