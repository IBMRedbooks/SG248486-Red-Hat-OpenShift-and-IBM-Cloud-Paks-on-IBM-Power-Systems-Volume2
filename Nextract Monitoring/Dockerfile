FROM python:3.6

ENV version v10

WORKDIR /scripts
COPY scripts/requirements.txt .
RUN apt update && pip install -r requirements.txt

RUN wget http://public.dhe.ibm.com/systems/power/community/aix/AIXpert_Blog/nextract_${version}.tar \
&& tar xvf nextract_${version}.tar

CMD ["python"]
