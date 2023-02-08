import json
import rina_package_drop as rpd
import rina_datarate as rd
import latency_test as rlt
import time

def write_json(data):
    t = round(time.time())
    with open(f'data-{t}.json', 'w') as file:
        json.dump(data, file, indent=4)

def create_json(title, x_name, x_unit, y_name, y_unit, series):
    id = title.replace(" ", "_").lower()

    json = {
        "id": id,
        "title": title,
        "axes": {
            "x": {
                "name": x_name,
                "unit": x_unit
            },
            "y": {
                "name": y_name,
                "unit": y_unit
            }
        },
        "series": series
    }
    return json


def main():
    test_results = []
    drop_package_test = rpd.main()
    datarate_test = rd.main()
    latency_test = rlt.main()

    for test in drop_package_test:
        for title in test:
            test_results.append(create_json(title, "pckg loss", "%", "datarate", "Mbit/s", test[title]))

    for test in datarate_test:
        for title in test:
            test_results.append(create_json(title, "nodes", "", "datarate", "Mbit/s", test[title]))

    for test in latency_test:
        for title in test:
            test_results.append(create_json(title, "nodes", "", "Latency", "ms", test[title]))

    write_json(test_results)
    
if __name__ == "__main__":
    main()

