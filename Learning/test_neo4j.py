from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "atom-william-carter-vibrate-press-9029"  # Replace with the password you set in the Neo4j Browser

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
try:
    driver.verify_connectivity()
    print("Successfully connected to Neo4j!")
except Exception as e:
    print(f"Failed to connect: {e}")
finally:
    driver.close()