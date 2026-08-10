from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def graph_search(intents):

    results = []


    # --------------------------------
    # Founder
    # --------------------------------

    if "founder" in intents:

        query = """
        MATCH (person:Person)-[:FOUNDED]->(company:Company)
        RETURN
            person.name AS person,
            "FOUNDED" AS relationship,
            company.name AS company
        """

        with driver.session() as session:

            records = session.run(query)

            for record in records:

                results.append({
                    "type": "founder",
                    "person": record["person"],
                    "relationship": record["relationship"],
                    "company": record["company"]
                })


    # --------------------------------
    # CEO
    # --------------------------------

    if "ceo" in intents:

        query = """
        MATCH (person:Person)-[:CEO_OF]->(company:Company)
        RETURN
            person.name AS person,
            "CEO_OF" AS relationship,
            company.name AS company
        """

        with driver.session() as session:

            records = session.run(query)

            for record in records:

                results.append({
                    "type": "ceo",
                    "person": record["person"],
                    "relationship": record["relationship"],
                    "company": record["company"]
                })


    # --------------------------------
    # Product
    # --------------------------------

    if "product" in intents:

        query = """
        MATCH (company:Company)-[:PRODUCES]->(product:Product)
        RETURN
            company.name AS company,
            "PRODUCES" AS relationship,
            product.name AS product
        """

        with driver.session() as session:

            records = session.run(query)

            for record in records:

                results.append({
                    "type": "product",
                    "company": record["company"],
                    "relationship": record["relationship"],
                    "product": record["product"]
                })


    return results