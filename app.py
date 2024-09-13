import streamlit as st
import psycopg2
import requests
from config import API_URL, POSTGRES_CONNECTION_STRING


st.title('Fake News Detection')

def predict_news(title, text, subject, date):
    """Make an API call to predict whether news is fake or not."""
    try:
        response = requests.post(API_URL, json={
            'title': title,
            'text': text,
            'subject': subject,
            'date': str(date)
        })
        response.raise_for_status()
        prediction = response.json().get('prediction')
        return prediction if prediction == 'fake' else True
    except requests.exceptions.HTTPError as e:
        st.error(f'HTTP error occurred: {e.response.status_code}')
    except requests.exceptions.RequestException:
        st.error('Failed to connect to the API')
    except Exception as e:
        st.error(f'An error occurred: {str(e)}')

def insert_article(title, text, subject, date, label, user_feedback):
    """Insert article and feedback into the database."""
    query = """
    INSERT INTO articles (title, text, subject, date, label, labelUser)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        with psycopg2.connect(POSTGRES_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (title, text, subject, date, label, user_feedback))
                conn.commit()
                st.success("Thank you for your feedback! Data has been saved.")
    except psycopg2.DatabaseError as e:
        st.error(f"Database error occurred: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Form to submit news details for prediction
with st.form("my_form"):
    title = st.text_input('News Title')
    text = st.text_area('News Text')
    subject = st.text_input('News Subject')
    date = st.date_input('Date')
    submitted = st.form_submit_button("Submit")

    if submitted:
        prediction = predict_news(title, text, subject, date)
        st.session_state['prediction'] = prediction
        st.session_state['submitted'] = True
        st.write('Prediction:', prediction)

# Check if the prediction has been made
if st.session_state.get('submitted', False):
    st.write("Prediction:", st.session_state['prediction'])

    # Form for feedback
    with st.form("feedback_form"):
        st.write("Do you agree with the prediction?")
        feedback = st.radio("Select True if you agree, or False if you disagree:", options=[True, False])
        feedback_submitted = st.form_submit_button("Submit Feedback")

        if feedback_submitted:
            insert_article(title, text, subject, date, st.session_state['prediction'], feedback)
