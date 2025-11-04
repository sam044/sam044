import datetime
import html

# Colors & font
ORANGE = "#f39c12"
BLUE   = "#3fa7ff"
GRAY   = "#d9d9d9"
BG     = "#0d1117"
FONT   = "Consolas, 'Courier New', monospace"

# Data (your values)
data = {
    "name": "Sam Flynn",
    "date": datetime.date.today().strftime("%b %d, %Y"),
    "location": "Northern Virginia (NoVA)",
    "education": "Computer Science & Mathematics Student",
    "age": "20 years",
    "prog": "Java, Python, C++",
    "comp": "HTML, JSON, LaTeX",
    "lang": "English",
    "hobbies": "Software Architecture, Algorithmic Design, Gaming, Weightlifting",
    "personal": "samuelpflynn1@gmail.com",
    "student": "spf16574@email.vccs.edu",
    "repos": "1",
    "commits": "000",
    "stars": "0",
    "followers": "0",
}

# Escape XML-reserved chars just in case (e.g., the & in CS & Math)
for k, v in data.items():
    if isinstance(v, str):
        data[k] = html.escape(v, quote=False)

# Positions
Y0   = 40
STEP = 30

# Header line with an em-dash written as \u2014 to avoid smart-char issues
header_text = f"{data['name']} &#8212; Updated {data['date']}"


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520"
  style="background-color:{BG};font-family:{FONT};">
  <style>
    .o {{ fill:{ORANGE}; font-weight:bold; }}
    .b {{ fill:{BLUE}; }}
    .t {{ fill:{GRAY}; }}
  </style>

  <!-- Header -->
  <text x="25" y="{Y0}" class="t">{header_text}</text>

  <!-- Body -->
  <text x="25"  y="{Y0+2*STEP}" class="o">Location:</text>
  <text x="260" y="{Y0+2*STEP}" class="b">{data['location']}</text>

  <text x="25"  y="{Y0+3*STEP}" class="o">Education:</text>
  <text x="260" y="{Y0+3*STEP}" class="b">{data['education']}</text>

  <text x="25"  y="{Y0+4*STEP}" class="o">Age:</text>
  <text x="260" y="{Y0+4*STEP}" class="b">{data['age']}</text>

  <text x="25"  y="{Y0+6*STEP}" class="o">Languages-Programming:</text>
  <text x="260" y="{Y0+6*STEP}" class="b">{data['prog']}</text>

  <text x="25"  y="{Y0+7*STEP}" class="o">Languages-Computer:</text>
  <text x="260" y="{Y0+7*STEP}" class="b">{data['comp']}</text>

  <text x="25"  y="{Y0+8*STEP}" class="o">Languages-Natural:</text>
  <text x="260" y="{Y0+8*STEP}" class="b">{data['lang']}</text>

  <text x="25"  y="{Y0+10*STEP}" class="o">Hobbies:</text>
  <text x="260" y="{Y0+10*STEP}" class="b">{data['hobbies']}</text>

  <text x="25"  y="{Y0+12*STEP}" class="o">Personal-Email:</text>
  <text x="260" y="{Y0+12*STEP}" class="b">{data['personal']}</text>

  <text x="25"  y="{Y0+13*STEP}" class="o">Student-Email:</text>
  <text x="260" y="{Y0+13*STEP}" class="b">{data['student']}</text>

  <text x="25"  y="{Y0+15*STEP}" class="o">GitHub Stats:</text>
  <text x="260" y="{Y0+15*STEP}" class="b">
    Repos {data['repos']} | Commits {data['commits']} | Stars {data['stars']} | Followers {data['followers']}
  </text>
</svg>
"""

with open("banner.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("✅ banner.svg generated")
