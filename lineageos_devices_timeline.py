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
    
    # Extract battery capacity
    battery_data = data.get("battery", {})
    battery_capacity = battery_data.get("capacity", "") if isinstance(battery_data, dict) else ""
    
    # Extract screen data
    screen_data = data.get("screen", {})
    screen_size = screen_data.get("size", "") if isinstance(screen_data, dict) else ""
    screen_resolution = screen_data.get("resolution", "") if isinstance(screen_data, dict) else ""
    
    # Extract RAM and Storage
    ram = data.get("ram", "")
    storage = data.get("storage", "")
    
    # Extract SoC
    soc = data.get("soc", "")
    
    list_data.append({
                         "type": data.get("type").title(),
                         "brand": data.get("vendor"),
                         "model": data.get("name"),
                         "release_date": str(formatted_release_date),
                         "versions": [str(x) for x in data.get("versions")],
                         "maintainers": data.get("maintainers"),
                         "codename": data.get("codename"),
                         "battery_capacity": str(battery_capacity) if battery_capacity else "",
                         "screen_size": str(screen_size) if screen_size else "",
                         "screen_resolution": screen_resolution if screen_resolution else "",
                         "ram": ram if ram else "",
                         "storage": storage if storage else "",
                         "soc": soc if soc else "",
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
        <th>Screen Size</th>
        <th>Screen Resolution</th>
        <th>Battery (mAh)</th>
        <th>RAM</th>
        <th>Storage</th>
        <th>SoC</th>
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
        <td>{data['screen_size'] + '"' if data['screen_size'] else ''}</td>
        <td>{data['screen_resolution']}</td>
        <td>{data['battery_capacity']}</td>
        <td>{data['ram']}</td>
        <td>{data['storage']}</td>
        <td>{data['soc']}</td>
        </tr>
    """ for data in sorted_list_data]) + "</tbody>\n"

date_update = datetime.today().strftime("%Y-%m-%d")

formatted_message = read_template("template.html").safe_substitute(
    {"date_update": date_update, "header": header, "table_data": table_data})
with open("docs/index.html", "w") as f:
    f.write(formatted_message)
