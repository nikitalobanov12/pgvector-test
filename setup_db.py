import psycopg
from pgvector.psycopg import register_vector

DB_CONFIG = "host=localhost port=5432 dbname=vecdb user=dev password=dev"


def create_connection():
    conn = psycopg.connect(DB_CONFIG)
    register_vector(conn)
    return conn


def setup_database():
    conn = psycopg.connect(DB_CONFIG)
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()

    register_vector(conn)

    cur.execute("DROP TABLE IF EXISTS documents")
    cur.execute("""
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding vector(384)
        )
    """)

    cur.execute(
        "CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Database setup complete!")


if __name__ == "__main__":
    setup_database()
