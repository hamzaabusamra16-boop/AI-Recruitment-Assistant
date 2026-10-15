from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)
def similarity(candidate_text, job_text):
    embeddings = model.encode([
        candidate_text,
        job_text
    ])
    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]
    return {
        "similarity_score": round(float(score) * 100, 2)
    }
def compare_requirement_similarity(requirement, evidence_text):
    embeddings = model.encode([
        requirement,
        evidence_text
    ])

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(float(score) * 100, 2)