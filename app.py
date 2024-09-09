import streamlit as st
import requests
from config import API_URL

st.title('Fake News Detection')

# Form to submit news details for prediction
with st.form("my_form"):
    title = st.text_input('News Title')
    text = st.text_area('News Text')
    subject = st.text_input('News Subject')
    date = st.date_input('Date')
    submitted = st.form_submit_button("Submit")

    if submitted:
        try:
            response = requests.post(API_URL, json={
                'title': title,
                'text': text,
                'subject': subject,
                'date': str(date)
            })
            response.raise_for_status()  # This will raise an exception for HTTP error codes
            prediction = response.json()
            st.write('Prediction:', prediction)

            # Store the prediction in session state to persist it across renders
            st.session_state.prediction = prediction
            st.session_state.submitted = True

        except requests.exceptions.HTTPError as e:
            st.error(f'HTTP error occurred: {e.response.status_code}')
        except requests.exceptions.RequestException as e:
            st.error('Failed to connect to the API')
        except Exception as e:
            st.error(f'An error occurred: {str(e)}')

# Check if the prediction has been made
if st.session_state.get('submitted', False):
    st.write("Prediction:", st.session_state.prediction)

    # Form for feedback
    with st.form("feedback_form"):
        st.write("Do you agree with the prediction?")
        feedback = st.radio("Select True if you agree, or False if you disagree:", options=[True, False])
        feedback_submitted = st.form_submit_button("Submit Feedback")

        if feedback_submitted:
            try:
                feedback_response = requests.post(f"{API_URL}/feedback", json={
                    'title': title,
                    'text': text,
                    'subject': subject,
                    'date': str(date),
                    'prediction': st.session_state.prediction,
                    'feedback': feedback
                })
                feedback_response.raise_for_status()
                st.success("Thank you for your feedback!")
            except requests.exceptions.RequestException as e:
                st.error("Failed to submit feedback.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
