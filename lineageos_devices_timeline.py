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
    print(formatted_data)
    list_data.append({
                         "type": data.get("type"),
                         "brand": data.get("vendor"),
                         "model": data.get("name"),
                         "release_date": str(formatted_release_date),
                     })

sorted_list_data = sorted(list_data, key=lambda x: (x['release_date'], x['brand'], x['model']), reverse=True)
print(sorted_list_data)

header = """
<thead>
    <tr>
        <th>Type</th>
        <th>Brand</th>
        <th>Model</th>
        <th>Release Date</th>
    </tr>
</thead>
"""

table_data = "<tbody>" + "\n".join([f"""
        <tr>
        <td>{data['type']}</td>
        <td>{data['brand']}</td>
        <td>{data['model']}</td>
        <td>{data['release_date']}</td>
        </tr>
    """ for data in sorted_list_data]) + "</tbody>\n"

date_update = datetime.today().strftime("%Y-%m-%d")

formatted_message = read_template("template.html").safe_substitute(
    {"date_update": date_update, "header": header, "table_data": table_data})
with open("docs/index.html", "w") as f:
    f.write(formatted_message)
