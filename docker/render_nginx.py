import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.environ.get("RENDER_NGINX_TEMPLATE_DIR", "/etc/openresty/")
OUTPUT_FILE = os.environ.get("RENDER_NGINX_OUTPUT_FILE", "/etc/openresty/nginx.conf")


def str_to_bool(v):
    if isinstance(v, str):
        if v.lower() == 'true':
            return True
        if v.lower() == 'false':
            return False
    return v


def main():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,
    )

    template = env.get_template("nginx.conf.j2")

    # Convert environment variables that look like booleans to actual booleans
    # so that Jinja2 evaluates them correctly.
    env_vars = {k: str_to_bool(v) for k, v in os.environ.items()}
    rendered = template.render(**env_vars)

    Path(OUTPUT_FILE).write_text(rendered)


if __name__ == "__main__":
    main()
