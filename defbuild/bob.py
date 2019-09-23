import os
import sys
import requests
import logging


DEFOLD_VERSION_URL = "https://gist.githubusercontent.com/Jerakin/801f6a71121095c467eaae9689d41828/raw/"


class Project:
    def __init__(self, config):
        self.config = config
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".builder", "cache")
        self.bob = config.get("config", "bob", fallback="")

    def final(self):
        self.config.set("config", "bob", self.bob)

        with open(os.path.join(self.cache_dir, "session"), 'w') as f:
            self.config.write(f)


def exists(project, sha):
    target = os.path.join(project.cache_dir, "bob", "bob_{}.jar".format(sha))
    if os.path.exists(target):
        return target
    return


def update(project, sha, force):
    target = os.path.join(project.cache_dir, "bob", "bob_{}.jar".format(sha))

    bob_exists = exists(project, sha)
    if bob_exists and not force:
        project.bob = bob_exists
        logging.info("Using cached version {}".format(get_version_from_sha(sha)))
    else:
        download(project.cache_dir, sha)
        project.bob = target
        logging.info("Bob set to {}".format(get_version_from_sha(sha)))


def download(cache, sha):
    if requests.head("http://d.defold.com/archive/{}/bob/bob.jar".format(sha)).status_code > 400:
        logging.error("Can't find bob version {}".format(sha))
        sys.exit(1)

    logging.info("Downloading new bob {}".format(get_version_from_sha(sha)))

    bob_directory = os.path.join(cache, "bob")
    bob_url = "http://d.defold.com/archive/{}/bob/bob.jar".format(sha)
    if not os.path.exists(bob_directory):
        os.makedirs(bob_directory, exist_ok=True)

    target = os.path.join(bob_directory, "bob_{}.jar".format(sha))
    r = requests.get(bob_url, stream=True)
    with open(target, "wb") as f:
        total_size = int(r.headers.get('content-length', 0))
        if total_size:
            dl = 0
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)

                # Progressbar
                done = int(50 * dl / total_size)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()
            sys.stdout.write("\n")
        else:
            f.write(r.content)


def beta():
    beta_info = requests.get("http://d.defold.com/beta/info.json").json()
    return beta_info["sha1"], beta_info["version"]


def warning(project):
    latest = requests.get("http://d.defold.com/stable/info.json").json()["sha1"]
    if latest not in project.bob:
        logging.info(
            "bob is out of date update with 'builder bob --update'")


def get_version_from_sha(sha):
    json_data = requests.get(DEFOLD_VERSION_URL).json()
    for x in json_data["versions"]:
        if x["sha1"] == sha:
            return x["version"]
    beta_sha, beta_version = beta()
    if beta_sha == sha:
        logging.info("Using beta version")
        return beta_version
    return "unknown"


def get_sha_from_version(version):
    json_data = requests.get(DEFOLD_VERSION_URL).json()
    for x in json_data["versions"]:
        if x["version"] == version:
            return x["sha1"]


def get_version_from_file_name(file_name):
    return get_version_from_sha(file_name.replace(".jar", "").split("bob_")[-1])