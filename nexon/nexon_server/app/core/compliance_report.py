from jinja2 import Environment, FileSystemLoader
import pdfkit


def generate_compliance_report(data: dict, output: str):
    env = Environment(loader=FileSystemLoader("app/templates"))
    html = env.get_template("compliance.html.j2").render(**data)
    pdfkit.from_string(html, output)
