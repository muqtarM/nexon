import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


class PipelineManager:
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)

    def list_templates(self) -> list[str]:
        return [d.name for d in Path("nexon_templates").iterdir() if (Path("nexon_templates")/d).is_dir()]

    def render(self, template: str, dest: Path, context: dict):
        tpl = self.env.get_template(f"{template}.pipeline.yaml.j2")
        context = tpl.render(**context)
        data = yaml.safe_load(context)
        # write files and subfolders
        for fname, body in data.get("files", {}).items():
            p = dest / fname
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
