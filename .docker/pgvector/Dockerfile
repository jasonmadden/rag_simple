
FROM postgres:15

RUN apt-get update && apt-get install -y postgresql-server-dev-15 build-essential git \
  && git clone https://github.com/pgvector/pgvector.git \
  && cd pgvector && make && make install
