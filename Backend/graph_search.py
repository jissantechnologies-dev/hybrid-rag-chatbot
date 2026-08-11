from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()


# --------------------------------
# Neo4j Configuration
# --------------------------------

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# --------------------------------
# Graph Search
# --------------------------------

def graph_search(question: str):

    results = []

    # --------------------------------
    # Generic graph query
    # --------------------------------

    query = """
    MATCH (source)-[relationship]->(target)

    WHERE
        toLower(coalesce(source.name, "")) CONTAINS toLower($question)
        OR
        toLower(coalesce(target.name, "")) CONTAINS toLower($question)

    RETURN
        labels(source) AS source_labels,
        source.name AS source,
        type(relationship) AS relationship,
        labels(target) AS target_labels,
        target.name AS target

    LIMIT 20
    """

    with driver.session() as session:

        records = session.run(
            query,
            question=question
        )

        for record in records:

            results.append({
                "source": record["source"],
                "source_labels": record["source_labels"],
                "relationship": record["relationship"],
                "target": record["target"],
                "target_labels": record["target_labels"]
            })

    return results