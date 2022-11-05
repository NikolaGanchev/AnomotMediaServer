FROM ubuntu:latest AS compile-image


ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3-pip \
    libjpeg-turbo8-dev \
    zlib1g-dev \
    libtiff5-dev \
    liblcms2-dev \
    libfreetype6-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libopenjp2-7-dev \
    libraqm0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
     ffmpeg && rm -rf /var/lib/apt/lists/*

COPY . .

COPY --from=compile-image /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]