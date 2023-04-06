FROM python:alpine3.17

# prevent Python from writing bytecode files
ENV PYTHONDONTWRITEBYTECODE 1

# run Python in unbuffered mode
ENV PYTHONUNBUFFERED 1

# define environment variables for the application path, input location, and output location
ENV APP_HOME /app
ENV INPUT_LOCATION /input
ENV OUTPUT_LOCATION /output

# If needed, update the package manager and install the GCC and G++ compilers
# RUN apk update && apk upgrade && apk add gcc g++

# copy the src directory to the image
COPY src $APP_HOME/

# copy the requirements.txt to the image
COPY requirements.txt $APP_HOME/

# set the working directory to the app directory
WORKDIR $APP_HOME

# If needed, upgrade pip
# RUN pip install --upgrade pip

# install the dependencies from the requirements.txt file
RUN pip install -r requirements.txt

# set the entrypoint for the container
ENTRYPOINT ["python", "-m", "digitalai.release.integration.wrapper"]
