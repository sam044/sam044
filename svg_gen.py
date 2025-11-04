from datetime import date
from lxml import etree

# Values you want to show (you can wire these to API later)
VALUES = {
    "location_data":  "Northern Virginia (NoVA)",
    "education_data": "Computer Science & Mathematics Student",  # literal OK; SVG has &amp; in template
    "age_data":       "20 years",
    "prog_data":      "Java, Python, C++",
    "comp_data":      "HTML, JSON, LaTeX",
    "lang_data":      "English",
    "hobbies_data":   "Software Architecture, Algorithmic Design, Gaming, Weightlifting",
    "personal_data":  "samuelpflynn1@gmail.com",
    "student_data":   "spf16574@email.vccs.edu",
    "stats_data":     "Repos 1 | Commits 000 | Stars 0 | Followers 0",
}

def set_text(root, element_id, text):
    el = root.find(f".//*[@id='{element_id}']")
    if el is not None:
        el.text = text

def main():
    fname = "banner.svg"
    tree = etree.parse(fname)
    root = tree.getroot()

    # Header line (keeps em dash entity already in SVG; we just swap the date)
    header = root.find(".//*[@id='header']")
    if header is not None:
        header.text = f"Sam Flynn — Updated {date.today().strftime('%b %d, %Y')}"

    # Fill fields
    for k, v in VALUES.items():
        set_text(root, k, v)

    tree.write(fname, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
    print("✅ banner.svg updated")
