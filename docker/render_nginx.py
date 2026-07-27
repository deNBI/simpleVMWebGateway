import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "/opt/simpleVMWebGateway/FastapiOpenRestyConfigurator"
OUTPUT_FILE = "/etc/openresty/nginx.conf"


def main():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
    )

    template = env.get_template("nginx.conf.j2")

    rendered = template.render(**os.environ)

    Path(OUTPUT_FILE).write_text(rendered)


if __name__ == "__main__":
    main()
