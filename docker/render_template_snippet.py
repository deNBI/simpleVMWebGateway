import argparse
import sys
import re
from pathlib import Path
from jinja2 import Template

def main():
    parser = argparse.ArgumentParser(description="Render a Nginx template snippet with dummy variables for security scanning.")
    parser.add_argument("template_path", help="Path to the Jinja2 template file")
    parser.add_argument("output_path", help="Path where the rendered snippet should be saved")
    parser.add_argument("--backend-id", help="Unique ID for the backend (defaults to filename)")
    parser.add_argument("--location-url", help="Unique location URL for the backend")
    args = parser.parse_args()

    # Generate a default backend_id based on the filename if not provided
    backend_id = args.backend_id or Path(args.template_path).stem

    # Sanitize the ID for use in URLs (replace non-alphanumeric characters with underscores)
    sanitized_id = re.sub(r'[^a-zA-Z0-9_-]', '_', backend_id)

    # Generate a default location_url based on the sanitized_id if not provided
    location_url = args.location_url or f"http://127.0.0.1:8080/{sanitized_id}"

    # Dummy variables for security scanning purposes
    dummy_vars = {
        "key_url": f"test-key-{sanitized_id}",
        "forc_backend_path": "./render_tmp/backends",
        "backend_id": backend_id,
        "owner": "test-user",
        "location_url": location_url,
    }

    try:
        template_content = Path(args.template_path).read_text()
        template = Template(template_content)
        rendered = template.render(**dummy_vars)
        Path(args.output_path).write_text(rendered)
    except Exception as e:
        print(f"Error rendering template {args.template_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
