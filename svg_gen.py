import datetime

orange = "#f39c12"
blue = "#3fa7ff"
gray = "#d9d9d9"

data = {
    "os": "Windows 11, Ubuntu 22.04",
    "location": "Northern Virginia (NoVA)",
    "education": "Computer Science &amp; Mathematics Student",
    "age": "20 years",
    "prog": "Java, Python, C++",
    "comp": "HTML, JSON, LaTeX",
    "lang": "English",
    "hobbies": "Software Architecture, Algorithmic Design, Weightlifting",
    "personal": "samuelpflynn1@gmail.com",
    "student": "spf16574@email.vccs.edu",
    "repos": "1",
    "commits": "000",
    "stars": "0",
    "followers": "0",
    "date": datetime.date.today().strftime("%b %d, %Y")
}

svg_template = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="550" style="background-color:#0d1117;font-family:'Consolas','Courier New',monospace;">
  <style>
    .o{{fill:{orange};font-weight:bold;}}
    .b{{fill:{blue};}}
    .t{{fill:{gray};}}
  </style>
  <text x="25" y="40" class="t">sam@flynn — Updated {data['date']}</text>
  <text x="25" y="80"  class="o">OS:</text> <text x="240" y="80" class="b">{data['os']}</text>
  <text x="25" y="110" class="o">Location:</text> <text x="240" y="110" class="b">{data['location']}</text>
  <text x="25" y="140" class="o">Education:</text> <text x="240" y="140" class="b">{data['education']}</text>
  <text x="25" y="170" class="o">Age:</text> <text x="240" y="170" class="b">{data['age']}</text>
  <text x="25" y="210" class="o">Languages.Programming:</text> <text x="350" y="210" class="b">{data['prog']}</text>
  <text x="25" y="240" class="o">Languages.Computer:</text> <text x="350" y="240" class="b">{data['comp']}</text>
  <text x="25" y="270" class="o">Languages.Natural:</text> <text x="350" y="270" class="b">{data['lang']}</text>
  <text x="25" y="310" class="o">Hobbies:</text> <text x="240" y="310" class="b">{data['hobbies']}</text>
  <text x="25" y="350" class="o">Contact.Personal:</text> <text x="350" y="350" class="b">{data['personal']}</text>
  <text x="25" y="380" class="o">Contact.Student:</text> <text x="350" y="380" class="b">{data['student']}</text>
  <text x="25" y="420" class="o">GitHub Stats:</text>
  <text x="240" y="420" class="b">Repos {data['repos']} | Commits {data['commits']} | Stars {data['stars']} | Followers {data['followers']}</text>
</svg>
"""

with open("banner.svg", "w", encoding="utf-8") as f:
    f.write(svg_template)
print("✅ banner.svg generated")
