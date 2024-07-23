from datetime import datetime
from pathlib import Path
import yaml
from string import Template

def read_template(filename: str) -> Template:
    with open(filename, "r") as f:
        content = f.read()
    return Template(content)

list_files = Path("lineage_wiki/_data/devices").glob("*.yml")
list_data = []
for index, file in enumerate(list_files, 1):
    with file.open() as f:
        data = yaml.safe_load(f)

    formatted_release_date = list(data.get('release')[0].values())[0] if isinstance(data.get('release'), list) else data.get('release')
    formatted_data = f"{data.get('type')} - {data.get('vendor')} - {data.get('name')} ({formatted_release_date})"
    list_data.append({
                         "type": data.get("type").title(),
                         "brand": data.get("vendor"),
                         "model": data.get("name"),
                         "release_date": str(formatted_release_date),
                         "versions": [str(x) for x in data.get("versions")],
                         "maintainers": data.get("maintainers"),
                         "codename": data.get("codename"),
                     })

sorted_list_data = sorted(list_data, key=lambda x: (x['release_date'], x['brand'], x['model']), reverse=True)

header = """
<thead>
    <tr>
        <th></th>
        <th>Brand</th>
        <th>Model</th>
        <th>Codename</th>
        <th>Release Date</th>
        <th>Supported Versions</th>
        <th>Status</th>
        <th>Type</th>
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
        <td>{'Maintained' if len(data['maintainers']) > 0 else 'Not maintained'}</td>
        <td>{data['type']}</td>
        </tr>
    """ for data in sorted_list_data]) + "</tbody>\n"

date_update = datetime.today().strftime("%Y-%m-%d")

formatted_message = read_template("template.html").safe_substitute(
    {"date_update": date_update, "header": header, "table_data": table_data})
with open("docs/index.html", "w") as f:
    f.write(formatted_message)
