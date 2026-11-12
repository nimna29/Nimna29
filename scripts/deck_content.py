"""All the copy for the Observation Deck README design. Edit here, then run
`python scripts/deck_assets.py` to regenerate ./assets/deck.

Icon keys ("logos:python", "simple:mongodb", ...) come from the portfolio's
stack catalog. A tool with `None` is drawn as a two-letter monogram. After
adding a tool that needs a new brand mark, run `python scripts/deck_extract.py`
once (it needs the portfolio repo checked out next to this one).
"""

NAME = "Nimna Niwarthana"
ROLES = ["Software Engineer", "AI/ML Developer", "Cybersecurity Specialist"]
TAGLINE = "I build secure software, train models and take malware apart."
SITE = "nimna-niwarthana.com"

# slug, kicker, title, sub line, icon
LINKS = [
    ("portfolio", "Visit", "Portfolio", "nimna-niwarthana.com", "globe"),
    ("linkedin", "Connect", "LinkedIn", "in/nimna-niwarthana", "in"),
    ("x", "Follow", "X / Twitter", "@niwarthananimna", "x"),
    ("coffee", "Support", "Buy me a coffee", "fuel the next build", "cup"),
]

# ── Crew profile ──────────────────────────────────────────────────────────
EDUCATION = [
    (["MSc Ethical Hacking", "& Cybersecurity"], "Abertay University, Scotland", "2025 - 2026"),
    (["BSc (Hons)", "Computer Security"], "University of Plymouth · NSBM", "2020 - 2023"),
]
CURRENTLY = [
    ("rocket", "Building", "Catalogie", "Full-stack & security engineering, live"),
    ("pulse", "Experience", "3+ years", "ML · software engineering · full-stack"),
]
PASSIONS = [("chip", "AI / ML"), ("shield", "Cybersecurity"), ("layers", "Full-stack dev"), ("chart", "Data science")]
FUN_FACT = "Dark mode isn't just easier on the eyes - it keeps the bugs away, because bugs are attracted to light."

# ── Tech arsenal: every category holds a multiple of 8 so each row is full ──
STACK = [
    ("Languages", [
        ("Python", "logos:python"), ("TypeScript", "logos:typescript-icon"), ("JavaScript", "logos:javascript"), ("C", "logos:c"),
        ("C#", "devicon:csharp"), ("Java", "devicon:java"), ("Dart", "logos:dart"), ("PHP", "devicon:php")]),
    ("Web & API", [
        ("React", "logos:react"), ("Next.js", "logos:nextjs-icon"), ("Vue", "logos:vue"), ("Node.js", "simple:nodedotjs"),
        ("Express", "devicon:express"), ("FastAPI", "logos:fastapi-icon"), ("Django", "logos:django-icon"), ("Flutter", "logos:flutter"),
        ("Tailwind CSS", "devicon:tailwindcss"), ("Bootstrap", "logos:bootstrap"), ("Vite", "simple:vite"), ("Jest", "logos:jest"),
        ("HTML5", "devicon:html5"), ("CSS3", "devicon:css3"), ("REST API", "logos:rest"), ("Keycloak", "simple:keycloak")]),
    ("AI / ML", [
        ("PyTorch", "logos:pytorch-icon"), ("TensorFlow", "logos:tensorflow"), ("Keras", "devicon:keras"), ("scikit-learn", "devicon:scikitlearn"),
        ("OpenCV", "simple:opencv"), ("YOLO", "simple:yolo"), ("Hugging Face", "simple:huggingface"), ("spaCy", "simple:spacy"),
        ("pandas", "devicon:pandas"), ("Jupyter", "logos:jupyter"), ("Google Colab", "devicon:googlecolab"), ("Vertex AI", "devicon:googlecloud"),
        ("LM Studio", "simple:lmstudio"), ("BERT", None), ("NLTK", None), ("Matplotlib", None)]),
    ("Gen AI & Agents", [
        ("Anthropic API", "simple:anthropic"), ("OpenAI API", "logos:openai-icon"), ("Claude Code", "simple:claudecode"), ("LangChain", "simple:langchain"),
        ("Ollama", "devicon:ollama"), ("GitHub Copilot", "logos:github-copilot"), ("Cursor", "devicon:cursor"), ("Gemini", "simple:googlegemini")]),
    ("Data, Cloud & DevOps", [
        ("PostgreSQL", "simple:postgresql"), ("MySQL", "simple:mysql"), ("MongoDB", "simple:mongodb"), ("Firebase", "logos:firebase-icon"),
        ("Oracle", "devicon:oracle"), ("MS SQL Server", None), ("Docker", "devicon:docker"), ("GitHub Actions", "logos:github-actions"),
        ("AWS", "devicon:amazonwebservices"), ("Google Cloud", "logos:google-cloud"), ("Azure", "logos:microsoft-azure"), ("Heroku", "logos:heroku-icon"),
        ("Vercel", "logos:vercel-icon"), ("Nginx", "logos:nginx"), ("Ubuntu", "logos:ubuntu"), ("Git", "logos:git-icon")]),
    ("Offensive Security", [
        ("Kali Linux", "devicon:kalilinux"), ("Parrot OS", "simple:parrotsecurity"), ("Burp Suite", "devicon:burpsuite"), ("Metasploit", "simple:metasploit"),
        ("OWASP ZAP", "simple:owasp"), ("Wireshark", "simple:wireshark"), ("Hashcat", "simple:hashcat"), ("Hack The Box", "simple:hackthebox"),
        ("TryHackMe", "simple:tryhackme"), ("Nmap", None), ("SQLmap", None), ("Hydra", None),
        ("BloodHound", None), ("John the Ripper", None), ("Gobuster", None), ("Aircrack-ng", None)]),
    ("Defence & Forensics", [
        ("Snort", "simple:snort"), ("pfSense", "devicon:pfsense"), ("Packet Tracer", "simple:cisco"), ("Ghidra", None),
        ("IDA", None), ("Volatility", None), ("Autopsy", None), ("FTK Imager", None)]),
    ("Tooling", [
        ("GitHub", "simple:github"), ("VS Code", "devicon:vscode"), ("Bash", "devicon:bash"), ("Postman", "simple:postman"),
        ("Jira", "logos:jira"), ("Figma", "devicon:figma"), ("IntelliJ IDEA", "logos:intellij-idea"), ("Android Studio", "devicon:androidstudio")]),
]
MONOGRAM = {"John the Ripper": "JR", "MS SQL Server": "MS", "FTK Imager": "FT", "Aircrack-ng": "AC", "BloodHound": "BH", "SQLmap": "SQ"}

# ── Featured work ─────────────────────────────────────────────────────────
# Every card carries a small animated miniature on its right side. `art` picks it:
#   "library"   stack of books + spinning disc    (catalogues, media, docs)
#   "scanner"   sample cube swept by a scan beam  (detection, analysis)
#   "database"  blocks dropping into a data store (datasets, pipelines, tools)
#   "chip"      microchip under a magnifier       (reverse engineering, research)
#   "rocket"    rocket on its pad                 (launches, shipped products)
#   "planet"    ringed planet - used when `art` is left out
# Change the text freely - the miniature stays. The build stops with a clear
# message if a description line or the chip row grows long enough to touch it.
PROJECTS = [
    dict(slug="catalogie", art="library", status="Live", title="Catalogie", tag="FULL-STACK · SECURITY · 2026 - NOW",
         lines=["One library for films, TV, games & books.", "Self-hosted PERN stack · 91 REST endpoints."],
         chips=["React", "TypeScript", "Express", "PostgreSQL"]),
    dict(slug="malditectist", art="scanner", status="Published", title="MalDitectist", tag="AI/ML RESEARCH · TAYLOR & FRANCIS",
         lines=["Ensemble malware detection - signature +", "anomaly models, 98.9% RF accuracy."],
         chips=["Python", "scikit-learn", "TensorFlow", "Django"]),
    dict(slug="malscraper", art="database", status="Tool", title="MalScraper", tag="MALWARE RESEARCH · DOCKER CLI",
         lines=["Turns raw Windows PE samples into", "ML-ready datasets: opcodes, n-grams."],
         chips=["Python", "Docker", "Capstone", "pefile"]),
    dict(slug="agenttesla", art="chip", status="Report", title="AgentTesla Analysis", tag="REVERSE ENGINEERING · .NET STEALER",
         lines=["Static, dynamic, memory & code analysis", "of a reflectively loaded payload."],
         chips=["Ghidra", "dnSpy", "Volatility 3", "Wireshark"]),
]

# key -> (kicker, title)
HEADINGS = {
    "arsenal": ("INVENTORY", "Tech Arsenal"),
    "work": ("MISSIONS", "Featured Work"),
    "activity": ("TELEMETRY", "Flight Activity"),
}
