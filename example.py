import os
from typing import List

from sentence_transformers import SentenceTransformer
import psycopg
from pgvector.psycopg import register_vector

DB_CONFIG = os.getenv("DATABASE_URL", "postgresql://dev:dev@localhost:5432/vecdb")


def create_connection(register: bool = True):
    conn = psycopg.connect(DB_CONFIG)
    if register:
        register_vector(conn)
    return conn


def add_document(content: str):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode(content)

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
        (content, embedding.tolist()),
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Added: {content}")


def batch_add(content: List[str]):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(content)
    conn = create_connection()
    cur = conn.cursor()

    for string, embedding in zip(content, embeddings):
        cur.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            (string, embedding.tolist()),
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Added:{content}")


def search_similar(query: str, limit: int = 5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query)

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content, 1 - (embedding <=> %s) AS similarity
        FROM documents
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (query_embedding.tolist(), query_embedding.tolist(), limit),
    )

    results = cur.fetchall()
    cur.close()
    conn.close()

    return results


def clear_database():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents")
    conn.commit()
    cur.close()
    conn.close()
    print("database cleared")


def inspect_database(depth: int = 10):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, embedding FROM documents LIMIT 5")
    results = cur.fetchall()
    cur.close()
    conn.close()

    print("\nRaw Database contents: ")
    print("=" * 50)
    for doc_id, content, embedding in results:
        print(f"ID: {doc_id}")
        print(f"Content: {content}")
        print(f"First {depth} dimensions: {embedding[:depth]}")
        print(f"Full Embedding Length: {len(embedding)}")
        print("-" * 50)


if __name__ == "__main__":
    clear_database()
    sample_docs = [
        "Python is a high-level programming language",
        "PostgreSQL is a powerful relational database",
        "Machine learning models can process natural language",
        "Vector databases enable semantic search",
        "Embeddings represent text as numerical vectors",
        "MongoDB is a not a relational database, behaving more like a graph",
    ]

    print("Adding sample documents...")
    batch_add(sample_docs)

    print("\n" + "=" * 50)
    query = "database technology"
    print(f"Searching for: '{query}'")
    print("=" * 50)

    results = search_similar(query)
    for i, (content, similarity) in enumerate(results, 1):
        print(f"\n{i}. {content}")
        print(f"   Similarity: {similarity:.4f}")
    inspect_database()
