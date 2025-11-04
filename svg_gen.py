import datetime

# Accent colors
ORANGE = "#f39c12"
BLUE   = "#3fa7ff"
GRAY   = "#d9d9d9"
BG     = "#0d1117"
FONT = "Consolas, 'Courier New', monospace"

data = {
    "name": "Sam Flynn",
    "date": datetime.date.today().strftime("%b %d, %Y"),
    "location": "Northern Virginia (NoVA)",
    "education": "Computer Science &amp; Mathematics Student",  # XML-escaped &
    "age": "20 years",
    "prog": "Java, Python, C++",
    "comp": "HTML, JSON, LaTeX",
    "lang": "English",
    "hobbies": "Software Architecture, Algorithmic Design, Weightlifting",
    "personal": "samuelpflynn1@gmail.com",
    "student": "spf16574@email.vccs.edu",
    # You can wire real stats later; placeholders are fine
    "repos": "1",
    "commits": "000",
    "stars": "0",
    "followers": "0",
}

# y positions (after removing the OS row, everything shifts up a notch)
Y0   = 40   # header line
STEP = 30   # line spacing

<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520"
  style="background-color:{BG};font-family:{FONT};">
  <style>
    .o {{ fill:{ORANGE}; font-weight:bold; }}
    .b {{ fill:{BLUE}; }}
    .t {{ fill:{GRAY}; }}
  </style>

  <!-- Header -->
  <text x="25" y="{Y0}" class="t">{data['name']} — Updated {data['date']}</text>

  <!-- Left labels (orange) and right values (blue) -->
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
