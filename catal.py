"""Convert Obsidian Notes to Notion"""


import os
from pathlib import Path

import requests
from markdown_it import MarkdownIt

import cons

# Constants
NOTION_TOKEN = cons.IIS_KEY
DATABASE_ID = cons.NOTION_DB_ID

# Headers for Notion API
HEADERS = {
    "Authorization": f"Bearer {cons.IIS_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# Initialize Markdown Parser
md_parser = MarkdownIt()

# Function to read Markdown files from Obsidian vault
def read_markdown_files(directory):
    files_data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                files_data[filename] = file.read()
    return files_data

# Convert Markdown content to Notion blocks
def markdown_to_notion_blocks(md_content):
    tokens = md_parser.parse(md_content)
    blocks = []
    for token in tokens:
        if token.type == "paragraph_open":
            continue
        elif token.type == "inline":
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": token.content}}
                    ]
                }
            })
        elif token.type == "heading_open":
            heading_level = int(token.tag[1])
            blocks.append({
                "object": "block",
                "type": f"heading_{heading_level}",
                f"heading_{heading_level}": {
                    "rich_text": [
                        {"type": "text", "text": {"content": tokens[tokens.index(token) + 1].content}}
                    ]
                }
            })
    return blocks

# Create a Notion page
def create_notion_page(title, blocks):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "title": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        "children": blocks
    }
    response = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    if response.status_code == 200:
        print(f"Page '{title}' created successfully.")
    else:
        print(f"Failed to create page '{title}'. Response: {response.text}")

# Main script to transfer notes
def transfer_notes_to_notion(vault_path):
    notes = read_markdown_files(vault_path)
    for filename, content in notes.items():
        title = filename[:-3]  # Remove the '.md' extension
        blocks = markdown_to_notion_blocks(content)
        create_notion_page(title, blocks)

# Run the script
if __name__ == "__main__":
    obsidian_vault_path = Path(r"C:\Users\apollo\iCloudDrive\iCloud~md~obsidian\Career\Red Team Association\InfiniteCTF")
    transfer_notes_to_notion(obsidian_vault_path)