import json
import rina_package_drop as rpd

def write_json(data):
    with open('data.json', 'a') as file:
        json.dump(data, file)

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

    for test in drop_package_test:
        for title in test:
            test_results.append(create_json(title, "pckg loss", "%", "datarate", "Mbit/s", test[title]))


    write_json(test_results)
    
if __name__ == "__main__":
    main()

