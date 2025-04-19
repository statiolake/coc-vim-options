import json
import os
import re
import urllib.request
from typing import Dict, List, Tuple


def fetch_vim_options() -> str:
    """
    Fetch the latest Vim options reference from GitHub using standard library.
    Falls back to a local file if the URL is not accessible.
    """
    url = "https://raw.githubusercontent.com/neovim/neovim/master/runtime/doc/quickref.txt"
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"Could not fetch from URL: {e}")
        # If we can't fetch, try to use a local file
        if os.path.exists("quickref.txt"):
            with open("quickref.txt", "r", encoding="utf-8") as f:
                return f.read()
        else:
            print("Warning: Could not fetch from URL and local file not found.")
            return ""


def extract_options_section(content: str) -> str:
    """Extract just the options section from the quickref.txt file."""
    # Find the options section which starts with *Q_op* and continues to the next section
    match = re.search(r"\*option-list\*(.*?)\-+\n\*Q_ur\*", content, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def parse_vim_options(options_text: str) -> List[Tuple[str, str, str]]:
    """
    Parse the Vim options section into structured data.
    Returns a list of tuples: (option_name, short_name, description)
    """
    # Find the option-list section which has the actual options
    # Regular expression to match option lines
    # Format: 'option_name'   'short_name'    description
    pattern = r"'(?P<long>[^']+)'(?:\s+)('(?P<short>[^']+)')?(?:\s+)(?P<description>.*?)(?:\n|$)"

    options = []
    for match in re.finditer(pattern, options_text):
        option_name = match.group("long")
        short_name = match.group("short") or option_name
        description = match.group("description").strip()

        options.append((option_name, short_name, description))

    return options


def generate_config_properties(options: List[Tuple[str, str, str]]) -> Dict:
    """Generate configuration properties for package.json."""
    properties = {}

    for option_name, short_name, description in options:
        property_name = f"vim-options.{option_name}"

        property_def = {
            # Set type to any
            "type": ["string", "number", "boolean", "array", "object", "null"],
            # Set default to null (no setting)
            "default": None,
            "description": f"{description}. (Vim option: '{option_name}', short: '{short_name}')",
        }

        properties[property_name] = property_def

    return properties


def generate_package_json(properties: Dict) -> str:
    """Generate the complete package.json content."""
    base_package = {
        "name": "@statiolake/coc-vim-options",
        "version": "0.3.0",
        "description": "Set vim options from coc-settings.json",
        "author": "statiolake <statiolake@gmail.com>",
        "license": "MIT",
        "main": "lib/index.js",
        "keywords": ["coc.nvim"],
        "engines": {"coc": "^0.0.80"},
        "scripts": {
            "lint": "eslint src --ext ts",
            "clean": "rimraf lib",
            "watch": "node esbuild.mjs --watch",
            "build": "node esbuild.mjs",
            "prepare": "node esbuild.mjs",
        },
        "prettier": {"singleQuote": True, "printWidth": 120, "semi": True},
        "devDependencies": {
            "@typescript-eslint/eslint-plugin": "^5.59.1",
            "@typescript-eslint/parser": "^5.59.1",
            "coc.nvim": "^0.0.80",
            "esbuild": "^0.17.18",
            "eslint": "^8.39.0",
            "eslint-config-prettier": "^8.8.0",
            "eslint-plugin-prettier": "^4.2.1",
            "prettier": "^2.8.8",
            "rimraf": "^5.0.0",
            "typescript": "^5.0.4",
        },
        "activationEvents": ["*"],
        "contributes": {
            "configuration": {
                "type": "object",
                "title": "Configure vim options",
                "properties": properties,
            },
            "commands": [],
        },
    }

    return json.dumps(base_package, indent=2)


def main():
    # Fetch the reference document
    content = fetch_vim_options()

    if not content:
        print("Error: Could not obtain Vim options reference")
        return

    # Extract and parse the options section
    options_section = extract_options_section(content)
    vim_options = parse_vim_options(options_section)

    for opt, _, _ in vim_options:
        print(f"{opt}")

    # Generate the configuration properties
    properties = generate_config_properties(vim_options)

    # Generate the package.json content
    package_json = generate_package_json(properties)

    # Write the result to a file
    with open("package.json", "w", encoding="utf-8") as f:
        f.write(package_json)

    print(f"Generated package.json with {len(properties)} Vim options")


if __name__ == "__main__":
    main()
