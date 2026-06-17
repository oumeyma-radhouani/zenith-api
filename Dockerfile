# starting with official linux + python env
FROM python:3.11-slim

# setting the working directory inside the container 
WORKDIR /app

#copy the requirements txt file 
COPY requirements.txt . 

# install the tools from requirements file
RUN pip install --no-cache-dir -r requirements.txt

#copy the main python file and everything else into the container
COPY . . 

#open window to talk to container on port 8000
EXPOSE 8000

#cmd to start the app when container turns on
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
