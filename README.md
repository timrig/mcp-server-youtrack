# MCP Server: Youtrack


## Tools
- `read_issues`: Suche nach Fehlern
- `read_articles`: Suche nach Artikeln
- `read_projects`: Suche nach Projekten
- `set_new_issue`: Erstellt einen neuen Fehler für ein Projekt


## Umgebungsvariablen
1. Kopiere die Datei .env.example
2. Nenne die neue Datei .env
3. Setze deine individuellen Umgebungsvariablen für *PERMANENT_TOKEN* und *BASE_URL*


## Installation
```bash
pip install -r requirements.txt
python -m app.main --transport stdio
```


## Claude Desktop config
```json
{
  "mcpServers": {
    "youtrack": {
      "command": "PATH_TO_PYTHON_EXE",
      "args": [
        "PATH_TO_main.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONPATH": "PATH_TO_MAIN_FOLDER",
        "PERMANENT_TOKEN": "YOUR_PERMANENT_TOKEN",
        "BASE_URL": "YOUR_BASE_URL"
      }
    }
  },
  "preferences": {
    "menuBarEnabled": false,
    "legacyQuickEntryEnabled": false
  }
}
```