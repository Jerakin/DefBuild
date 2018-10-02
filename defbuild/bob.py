import os
import sys
import requests
import logging


DEFOLD_VERSION_URL = "https://gist.githubusercontent.com/Jerakin/801f6a71121095c467eaae9689d41828/raw/2e95e14ddb4b893032fed98021ec5e8ef510631c/defold_version"


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
        logging.error("Can't find version {} of bob, supply valid version".format(sha))
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
    return "unknown"


def get_sha_from_version(version):
    json_data = requests.get(DEFOLD_VERSION_URL).json()
    for x in json_data["versions"]:
        if x["version"] == version:
            return x["sha1"]


def get_version_from_file_name(file_name):
    return get_version_from_sha(file_name.replace(".jar", "").split("bob_")[-1])