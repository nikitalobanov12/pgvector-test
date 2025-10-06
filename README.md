example of how vector embeddings work using plain text embeddings, the model takes the plain text, converts it into a vector representation and than stores the string as a 384-dimensional vector

The point of this was for me to better understand embedding models and how the vectors get stored in a database

![image](/demo.png)
[pgvector docs][https://github.com/pgvector/pgvector]
[pgvector python postgres adapter][https://github.com/pgvector/pgvector-python?tab=readme-ov-file#psycopg-3]
[sentence transformers][https://sbert.net/]

1. **Start PostgreSQL with pgvector:**

   ```bash
   docker-compose up -d
   ```

2. Start the Python Virtual Environment

```bash
python3 -m venv venv
```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**

   ```bash
   python setup_db.py
   ```

5. **Run the example:**

   ```bash
   python example.py
   ```
