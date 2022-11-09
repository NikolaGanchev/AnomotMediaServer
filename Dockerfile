FROM ubuntu:latest AS compile-image

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3-pip  \
    python3.10-venv \
    build-essential  \
    gcc \
    libjpeg-turbo8-dev \
    zlib1g-dev \
    liblcms2-dev \
    libwebp-dev \
    libopenjp2-7-dev \
     && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --no-deps --no-cache-dir -r requirements.txt \
     && CFLAGS="${CFLAGS} -mavx2" pip install --upgrade --no-cache-dir --force-reinstall --no-binary :all: --compile Pillow-SIMD==9.0.0.post1

FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends  \
    python3-pip \
    libjpeg-turbo8-dev \
    zlib1g-dev \
    liblcms2-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    clamav \
    clamav-daemon \
    && apt-get -y autoremove && rm -rf /var/lib/apt/lists/*

RUN freshclam

COPY --from=mwader/static-ffmpeg:5.1.2 /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg:5.1.2 /ffprobe /usr/local/bin/
COPY --from=compile-image /venv /venv

ENV PATH="/venv/bin:$PATH"

WORKDIR /app

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]