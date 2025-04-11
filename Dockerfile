FROM python:3.12.10-slim

RUN apt-get update \
    && apt-get install -y opam wget m4 unzip librsvg2-bin curl bubblewrap

RUN opam init -y \
    && opam switch create 5.2.0 -y \
    && eval $(opam env) \
    && opam remote add grew "https://opam.grew.fr" -y \
    && opam install grew -y

RUN opam update && opam upgrade

COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR /app/flask
EXPOSE 8000

ENV OPAM_SWITCH_PREFIX='/root/.opam/5.2.0'
ENV CAML_LD_LIBRARY_PATH='/root/.opam/5.2.0/lib/stublibs:/root/.opam/5.2.0/lib/ocaml/stublibs:/root/.opam/5.2.0/lib/ocaml'
ENV OCAML_TOPLEVEL_PATH='/root/.opam/5.2.0/lib/toplevel'
ENV MANPATH=':/root/.opam/5.2.0/man'
ENV PATH='/root/.opam/5.2.0/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

CMD ["gunicorn", "app:app"]
