from neo4j import GraphDatabase
from groq import Groq
import json
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Initialize Groq agent
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Neo4j driver
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "system123"
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
db = driver.session(database="memorygraph")


system_prompt = """
You are a Memory-Aware AI Agent using Neo4j to store relational knowledge.
Follow a step-by-step approach: plan → action → observe → output.
Rules:
- Analyze the user query to detect relational info (entity-relation-value).
- If no relational fact is detected → exit.
- Decide dynamically whether to insert a new node/relation or update existing one.
- Perform the database operation in Neo4j.
- Respond step-by-step in JSON format.

Output JSON Format:
{
    "step": "plan|action|observe|output",
    "content": "description of reasoning or output",
    "function": "optional function name if step is action",
    "input": "optional input for function"
}
"""

messages = [{"role": "system", "content": system_prompt}]




def is_unique_relation_dynamic(entity: str, relation: str) -> bool:
    """
    Ask Groq if this relation should be unique per entity.
    Returns True if unique, False if multi-valued.
    """
    prompt = f"""
    You are a reasoning agent.
    Decide whether the relation '{relation}' for entity '{entity}' is UNIQUE
    (only one value per entity) or MULTI-VALUED (can have multiple values).
    Answer ONLY with 'unique' or 'multi'.
    """
    completion = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0
    )
    answer = completion.choices[0].message.content.strip().lower()
    return answer == "unique"

def extract_relation(query: str):
    """
    Extract relational facts from the user query.
    Returns a list of dicts with entity, relation, value, or empty list.
    """
    prompt = f"""
    You are a Memory-Aware Fact Extraction Agent.
    Extract relational facts from this user query in strict JSON format.
    Only output JSON, no explanations.

    Format:
    {{
        "relations": [
            {{"entity": "...", "relation": "...", "value": "..."}}
        ]
    }}

    Examples:
    - "I am Anshul" → {{"relations": [{{"entity": "Anshul", "relation": "name", "value": "Anshul"}}]}}
    - "I live in Pune" → {{"relations": [{{"entity": "Anshul", "relation": "lives_in", "value": "Pune"}}]}}

    User query: {query}
    """
    completion = groq.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )
    response_text = completion.choices[0].message.content

    # Extract first {...} JSON block
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not match:
        return None

    try:
        relations = json.loads(match.group(0)).get("relations", [])
    except json.JSONDecodeError:
        relations = []

    return relations if relations else None

def execute_db_action(relation: dict):
    """
    Step 2 & 3: Decide insert/update and execute in Neo4j
    """
    entity = relation["entity"]
    rel = relation["relation"]
    value = relation["value"]

    # Check if relation exists
    existing = db.run(
        f"MATCH (e:Entity {{name:$entity}})-[r:{rel.upper()}]->(v) RETURN v.name AS value",
        entity=entity
    ).data()

    if existing:
        if is_unique_relation_dynamic(entity, rel):
            # Update existing relation
            query = f"""
            MATCH (e:Entity {{name:$entity}})-[r:{rel.upper()}]->(v)
            SET v.name = $value
            """
            db.run(query, entity=entity, value=value)
            return f"Updated {rel} for {entity} to {value}."
        else:
            # Insert as multi-valued
            query = f"""
            MATCH (e:Entity {{name:$entity}})
            MERGE (v:Value {{name:$value}})
            MERGE (e)-[:{rel.upper()}]->(v)
            """
            db.run(query, entity=entity, value=value)
            return f"Inserted new {rel} relation for {entity}."
    else:
        # Insert new relation
        query = f"""
        MERGE (e:Entity {{name:$entity}})
        MERGE (v:Value {{name:$value}})
        MERGE (e)-[:{rel.upper()}]->(v)
        """
        db.run(query, entity=entity, value=value)
        return f"Inserted new {rel} relation for {entity}."


# ----------------------------
# Main loop
# ----------------------------
while True:
    user_query = input("> ")
    messages.append({"role": "user", "content": user_query})

    # Step 1: Plan
    relations = extract_relation(user_query)
    if not relations:
        print(json.dumps({"step": "output", "content": "No relational fact detected. Exiting."}, indent=2))
        continue

    for relation in relations:
        # Plan step
        plan_msg = {
            "step": "plan",
            "content": f"Detected relation: {relation}. Will decide whether to insert or update in Neo4j."
        }
        print(json.dumps(plan_msg, indent=2))
        messages.append({"role": "assistant", "content": json.dumps(plan_msg)})

        # Action step
        action_msg = {
            "step": "action",
            "function": "execute_db_action",
            "input": relation
        }
        print(json.dumps(action_msg, indent=2))
        messages.append({"role": "assistant", "content": json.dumps(action_msg)})

        # Execute DB action
        output = execute_db_action(relation)

        # Observe step
        observe_msg = {
            "step": "observe",
            "content": output
        }
        print(json.dumps(observe_msg, indent=2))
        messages.append({"role": "assistant", "content": json.dumps(observe_msg)})

        # Output step
        final_msg = {
            "step": "output",
            "content": output
        }
        print(json.dumps(final_msg, indent=2))
        messages.append({"role": "assistant", "content": json.dumps(final_msg)})

# Optional: Close Neo4j session if needed
# db.close()
# driver.close()
