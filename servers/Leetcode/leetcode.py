import requests
from bs4 import BeautifulSoup

url = "https://leetcode.com/graphql"

query = """
query getQuestionDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionIdk
    questionFrontendId
    title
    content
    difficulty
    topicTags {
      name
      slug
    }
    exampleTestcases
  }
}
"""

variables = {"titleSlug": "minimum-score-triangulation-of-polygon"}

resp = requests.post(url, json={"query": query, "variables": variables})
data = resp.json()
q = data["data"]["question"]

# clean HTML -> plain text
soup = BeautifulSoup(q["content"], "html.parser")
description = soup.get_text("\n", strip=True)

# format output
print(f"[{q['difficulty']}] {q['questionFrontendId']}. {q['title']}")
print("Tags:", ", ".join(tag["name"] for tag in q["topicTags"]))
print("\nDescription:\n", description)

print("\nExamples:")
for ex in q["exampleTestcases"].split("\n"):
    print(" ", ex)
