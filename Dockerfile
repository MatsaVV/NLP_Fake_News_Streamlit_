# python base image in the container from Docker Hub
FROM python:3.10.6-buster

# set the working directory in the container to be /app
WORKDIR /app

# copy the necessary files to the /app folder in the container
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY app.py app.py
COPY utils.py utils.py
COPY config.py config.py

# install the packages from the Pipfile in the container
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# expose the port Streamlit uses
EXPOSE 8501

# execute the command to start the Streamlit app
CMD ["pipenv", "run", "streamlit", "run", "app.py", "--server.port", "$PORT", "--server.address", "0.0.0.0"]
