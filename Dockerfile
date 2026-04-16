FROM python:3.8
WORKDIR /app
ENV SECRET_KEY=password123
ENV DB_PASSWORD=admin
ENV API_KEY=sk-1234567890abcdef
ENV DEBUG=true
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py migrate --run-syncdb 2>/dev/null || true
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
