from typing import Any

from zensical.extensions.macros import MacroEnv


def define_env(env: MacroEnv):
    @env.macro
    def parameters_table(component: dict[str, Any], name: str):
        if not component:
            return f"""<div class="admonition danger">
            <p class="admonition-title">Error</p>
            <p>Component <code>{name or "unknown"}</code> not found or data not provided.</p>
            </div>
            """
        title = f"""<div class="component-parameters-title">
        Parameters for <code>{name}</code>
        </div>"""

        table = """|Parameter|Type|Description|\n|-|-|-|\n"""

        for arg_name, info in component["arguments"].items():
            arg_type = info.get("type", "any").replace("|", "&#124;")
            description = info["description"].replace("|", "&#124;")
            table += f"""|`{arg_name}`|{arg_type}|{description}|\n"""

        return title + table
