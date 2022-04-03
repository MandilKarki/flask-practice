FROM python:3.8
#set the working directory to app
WORKDIR /app

#copy local contents into the container
COPY requirements.txt /app


#Install all the required dependcies
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000
CMD ["python", "main.py"]

