import streamlit as st
import psycopg2
from config import API_URL, POSTGRES_CONNECTION_STRING
import requests

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
            # Call the API for prediction
            response = requests.post(API_URL, json={
                'title': title,
                'text': text,
                'subject': subject,
                'date': str(date)
            })
            response.raise_for_status()  # Raise error for bad HTTP responses
            prediction = response.json()
            label = prediction.get('prediction')  # Assuming the API returns a 'label' for prediction

            if label == 'fake':
                label = False
            else:
                label = True

            st.write('Prediction:', label)

            st.session_state.prediction = label
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
                # Connect to the PostgreSQL database
                conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
                cur = conn.cursor()

                # Insert feedback and article data into the 'articles' table
                insert_query = """
                INSERT INTO articles (title, text, subject, date, label, labelUser)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_query, (
                    title,  # The title of the article
                    text,   # The content of the article
                    subject,  # The subject of the article
                    date,   # The date of the article
                    st.session_state.prediction,  # The predicted label (True or False)
                    feedback  # User feedback on the label (True or False)
                ))
                conn.commit()

                # Close connection
                cur.close()
                conn.close()

                st.success("Thank you for your feedback! Data has been saved.")

            except psycopg2.DatabaseError as e:
                st.error(f"Database error occurred: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
