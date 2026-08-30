import os

from dotenv import load_dotenv
from google import genai
from sklearn.metrics.pairwise import cosine_similarity


# Load variables from .env
load_dotenv()


# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env file")


# Create Gemini client
client = genai.Client(
    api_key=api_key
)


# --------------------------------------------------
# CREATE EMBEDDING
# --------------------------------------------------

def embed(text: str) -> list[float]:
    """
    Convert text into an embedding vector.
    """

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return result.embeddings[0].values


# --------------------------------------------------
# FIND SIMILAR COMPLAINTS
# --------------------------------------------------

def find_similar(new_vector, stored_vectors, threshold=0.80):
    """
    Compare a new vector with stored vectors.

    Returns complaints whose similarity is
    greater than or equal to the threshold.
    """

    matches = []

    for item in stored_vectors:

        similarity = cosine_similarity(
            [new_vector],
            [item["vector"]]
        )[0][0]

        if similarity >= threshold:

            matches.append({
                "id": item["id"],
                "text": item["text"],
                "cluster_id": item.get("cluster_id"),
                "similarity": float(similarity)
            })

    # Highest similarity first
    matches.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return matches


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    text1 = "A water pipe is broken near the Main Market."

    text2 = "There is a leaking water pipeline near Main Market."

    text3 = "Many children are dropping out of school."

    vector1 = embed(text1)
    vector2 = embed(text2)
    vector3 = embed(text3)

    similarity_1_2 = cosine_similarity(
        [vector1],
        [vector2]
    )[0][0]

    similarity_1_3 = cosine_similarity(
        [vector1],
        [vector3]
    )[0][0]

    print("\nEmbedding generated successfully!")

    print("Vector length:", len(vector1))

    print(
        "\nSimilarity between water complaints:",
        round(float(similarity_1_2), 4)
    )

    print(
        "Similarity between water and education complaint:",
        round(float(similarity_1_3), 4)
    )