from jinja2 import Template
import requests, os, datetime

USER = os.getenv("USER_NAME", "sam044")
TOKEN = os.getenv("ACCESS_TOKEN")

headers = {"Authorization": f"token {TOKEN}"}
user_data = requests.get(f"https://api.github.com/users/{USER}", headers=headers).json()

repos_resp = requests.get(f"https://api.github.com/users/{USER}/repos", headers=headers)
repos_data = repos_resp.json() if repos_resp.status_code == 200 else []

stars = sum((repo.get("stargazers_count", 0) for repo in repos_data if isinstance(repo, dict)), 0)
commits = "000"  # placeholder
followers = user_data.get("followers", 0)
repos = user_data.get("public_repos", 0)

banner = f"Updated automatically • {datetime.date.today().strftime('%b %d, %Y')}"

template_text = open("template.md").read()
template = Template(template_text)
readme_content = template.render(
    banner=banner,
    age="20 years",
    repos=repos,
    commits=commits,
    stars=stars,
    followers=followers,
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)
