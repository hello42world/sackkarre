from lxml import etree

import json
import jsonpath_ng
from urllib.request import urlopen
import probe_spec

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def foo():
    url = 'https://www.lidl.de/p/parkside-plasmaschneider-pps-40-b3-4-4-5-bar/p100342928'

    parser = etree.HTMLParser()
    doc = etree.parse(urlopen(url), parser)
    res: list = doc.xpath("//script[@data-hid='json_data_product']")
    if len(res) == 0:
        raise "xpath failed"
    json_str: str = res[0].text

    json_data = json.loads(json_str)
    json_path = jsonpath_ng.parse('$.offers[0].price')
    match = json_path.find(json_data)
    if len(match) == 0:
        raise "jsonpath failed"

    price: float = float(match[0].value)
    print("id value is ", price)




def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    #foo()
    probe_spec.load('spec.yaml')



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
