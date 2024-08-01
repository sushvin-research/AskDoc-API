FROM ubuntu:22.04
RUN apt update && apt install -y python3.10
RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
RUN apt install -y ttf-mscorefonts-installer
RUN apt install -y python3-pip
RUN apt install -y wget
RUN apt install -y libgdiplus
RUN python3.10 -m pip install --upgrade pip
RUN wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
RUN dpkg -i ./libssl1.1_1.1.0g-2ubuntu4_amd64.deb
RUN rm -rf libssl1.1_1.1.0g-2ubuntu4_amd64.deb

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY AskDoc-API/ /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install aspose-words

RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xvJf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN cp wkhtmltox/bin/wkhtmlto* /usr/bin/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]