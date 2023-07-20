FROM python:3.9.6

WORKDIR /usr/src/app

# RUN apt-get update -qq && apt-get install -y \
#     # packages required by wkhtmlto*:
#     xfonts-base \
#     xfonts-75dpi \
#     pdftk
    # ...other custom packages...

# RUN curl -L#o wkhtmltopdf.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb
# RUN dpkg -i wkhtmltopdf.deb; apt-get install -y -f

# Remember to clean your package manager cache to reduce your custom image size...
RUN apt-get clean all \
    && rm -rvf /var/lib/apt/lists/*

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY . /usr/src/app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNUNBUFFERRED 1

# EXPOSE 8001

# ENTRYPOINT []
CMD python3 ./manage.py makemigrations && python3 ./manage.py migrate && python3 ./manage.py runserver 0.0.0.0:8002
