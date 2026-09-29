FROM python:3.11-slim
WORKDIR /app
COPY ex3-flash-sale.py .
RUN pip install --no-cache-dir flask gunicorn
CMD ["gunicorn","-b","0.0.0.0:5000","ex3-flash-sale:app","--workers","1","--threads","2"]
