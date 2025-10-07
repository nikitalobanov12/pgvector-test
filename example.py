from sentence_transformers import SentenceTransformer
import psycopg
from pgvector.psycopg import register_vector
from typing import List

DB_CONFIG = "host=localhost port=5432 dbname=vecdb user=dev password=dev"


def create_connection():
    conn = psycopg.connect(DB_CONFIG)
    register_vector(conn)
    return conn


def add_document(content: str):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode(content)

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
        (content, embedding),
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
            (string, embedding),
        )
    conn.commit()
    cur.close()
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
        (query_embedding, query_embedding, limit),
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
    print("datbase cleared")


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
