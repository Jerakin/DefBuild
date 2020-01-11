import requests
import json
import os
from html.parser import HTMLParser

_url = "http://d.defold.com/stable/"
_latest = "http://d.defold.com/stable/info.json"
_beta = "http://d.defold.com/beta/info.json"
version_json = os.path.join(os.path.expanduser("~"), ".builder", "cache", "version.json")


class _UpdateVersionJSON(HTMLParser):
    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, raw_data):
        if "var model" in raw_data[:100]:
            new = {"versions": []}
            data = raw_data[raw_data.find("{"):]
            data = data[:data.find(r"\n")]
            json_data = json.loads(data)
            for x in json_data["releases"]:
                entry = {"version":x["tag"], "sha1":x["sha1"]}
                new["versions"].append(entry)
            with open(version_json, "w") as fp:
                json.dump(new, fp, indent=4, sort_keys=True)


def update():
    response = requests.get(_url)
    if response.status_code in [200]:
        parser = _UpdateVersionJSON()
        parser.feed(str(response.content))


def latest():
    response = requests.get(_latest)
    if response.status_code in [200]:
        return response.json()["version"]


def update_required():
    if os.path.exists(version_json):
        new_version = latest()
        with open(version_json, "r") as fp:
            version_data = json.load(fp)

        if new_version not in version_data:
            return True
    return False


def beta():
    beta_info = requests.get(_beta).json()
    return beta_info["sha1"], beta_info["version"]


def get(auto_update=False):
    version_data = {}
    if os.path.exists(version_json):
        with open(version_json, "r") as fp:
            version_data = json.load(fp)
    elif auto_update:
        update()
        return get()
    return version_data