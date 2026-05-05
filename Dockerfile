FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies directly to avoid issues with requirements files
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic==1.10.12 \
    numpy \
    pandas \
    scikit-learn \
    xgboost \
    joblib \
    python-dotenv \
    streamlit \
    requests \
    psycopg2-binary \
    tensorflow

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
