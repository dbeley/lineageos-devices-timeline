from datetime import datetime
from pathlib import Path
import subprocess
import yaml
from string import Template

def read_template(filename: str) -> Template:
    with open(filename, "r") as f:
        content = f.read()
    return Template(content)

def get_first_commit_dates() -> dict:
    result = subprocess.run(
        ["git", "-C", "lineage_wiki", "log", "--all", "--diff-filter=A", "--name-only",
         "--format=COMMIT_DATE:%ai", "--", "_data/devices/"],
        capture_output=True, text=True
    )
    dates = {}
    current_date = None
    for line in result.stdout.splitlines():
        if line.startswith("COMMIT_DATE:"):
            current_date = line.split("COMMIT_DATE:")[1].strip().split(" ")[0]
        elif line.endswith(".yml"):
            filename = line.split("/")[-1]
            if filename not in dates:
                dates[filename] = current_date
    return dates

first_commit_dates = get_first_commit_dates()

list_files = Path("lineage_wiki/_data/devices").glob("*.yml")
list_data = []
for index, file in enumerate(list_files, 1):
    with file.open() as f:
        data = yaml.safe_load(f)

    formatted_release_date = list(data.get('release')[0].values())[0] if isinstance(data.get('release'), list) else data.get('release')
    first_supported = first_commit_dates.get(file.name, "Unknown")
    maintainers = data.get("maintainers")
    if maintainers:
        maintainers_str = ", ".join(maintainers)
    else:
        maintainers_str = "Not maintained"
    list_data.append({
                         "type": data.get("type").title(),
                         "brand": data.get("vendor"),
                         "model": data.get("name"),
                         "release_date": str(formatted_release_date),
                         "first_supported": first_supported,
                         "versions": [str(x) for x in data.get("versions")],
                         "maintainers": maintainers_str,
                         "codename": data.get("codename"),
                     })

header = """
<thead>
    <tr>
        <th></th>
        <th class="sortable">Brand</th>
        <th class="sortable">Model</th>
        <th class="sortable">Codename</th>
        <th class="sortable" data-column="release_date" data-default-sort="desc">Device Release Date</th>
        <th class="sortable">Supported Versions</th>
        <th class="sortable" data-column="first_supported">LineageOS Since</th>
        <th class="sortable">Maintainers</th>
        <th class="sortable">Type</th>
    </tr>
</thead>
"""

# https://wiki.lineageos.org/images/devices/salami.png
table_data = "<tbody>" + "\n".join([f"""
        <tr>
        <td><img loading='lazy' width='50' src='https://wiki.lineageos.org/images/devices/{data['codename']}.png' alt=''/></td>
        <td>{data['brand']}</td>
        <td><a href='https://wiki.lineageos.org/devices/{data['codename']}'>{data['model']}</a></td>
        <td>{data['codename']}</td>
        <td>{data['release_date']}</td>
        <td>{', '.join(data['versions'])}</td>
        <td>{data['first_supported']}</td>
        <td>{data['maintainers']}</td>
        <td>{data['type']}</td>
        </tr>
    """ for data in list_data]) + "</tbody>\n"

date_update = datetime.today().strftime("%Y-%m-%d")

formatted_message = read_template("template.html").safe_substitute(
    {"date_update": date_update, "header": header, "table_data": table_data})
with open("docs/index.html", "w") as f:
    f.write(formatted_message)
