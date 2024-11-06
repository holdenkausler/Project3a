#Use an official python image as base image
FROM python:3.8
#Set working directory in container to /app
WORKDIR /app

#Copy contents of the current directory in the container /app directory
COPY . /app

#Upgrade pip
RUN pip install --upgrade pip

#Install needed packages
RUN pip install --no-cache-dir -r requirements.txt

#set the default commands to run when starting the container
CMD ["python", "app.py"]