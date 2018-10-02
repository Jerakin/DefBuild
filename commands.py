import os
import sys
import bob as _bob
import time
import shutil
import logging
import requests
from subprocess import call


def build(project):
    logging.info("Building project {}".format(project.name))
    if not project.bob:
        logging.error("Can't find a bob version, download with 'builder bob --update'")
        sys.exit(1)

    command = ["java", "-jar", project.bob, "--archive", "--platform", project.platform, "--texture-compression", "true", "--debug", "--bundle-output", project.output]

    if project.report:
        command.extend(["--build-report-html", os.path.join(project.cache_dir, "report.html")])

    if project.platform == "armv7-android":
        project.android_build = os.path.join(project.output, project.name, "{}.apk".format(project.name))
    else:
        project.ios_build = os.path.join(project.output, "{}.ipa".format(project.name))
        if not project.identity:
            logging.error("""Please set a identity with 'set config identity "iPhone Developer: My Identity"'""")
        if not project.provision:
            logging.error(
                "Please set a mobile provision with 'set config provision /path/to/mobile_provision.mobileprovision'")
        if not project.provision or not project.identity:
            sys.exit(1)

        command.extend(["--identity", project.identity, "-mp", project.provision])

    if not project.quick:
        command.extend(["distclean"])

    command.extend(["build", "bundle"])
    start_time = time.time()
    call(command)
    m, s = divmod(time.time() - start_time, 60)
    logging.info("Building done in {:.0f}:{:.0f}".format(m, s))

    if project.report:
        import webbrowser
        webbrowser.open("file://" + os.path.join(project.cache_dir, "report.html"))


def install(project):
    if project.force:
        uninstall(project)

    if project.platform == "armv7-android":
        bundle = project.android_build
        command = ["adb", "install", bundle]
    else:
        bundle = project.ios_build
        command = ["ideviceinstaller", "-i", bundle]

    logging.info("Installing {}".format(os.path.basename(bundle)))
    if not shutil.which(command[0]):
        logging.error("Can not find dependency {}".format(command[0]))
        sys.exit(-1)
    call(command)


def uninstall(project):
    if project.platform == "armv7-android":
        logging.info("Uninstalling {}".format(project.android_id))
        command = ["adb", "uninstall", project.android_id]
    else:
        logging.info("Uninstalling {}".format(project.ios_id))
        command = ["ideviceinstaller", "-U", project.ios_id]

    if not shutil.which(command[0]):
        logging.error("Can not find dependency {}".format(command[0]))
        sys.exit(-1)

    call(command)


def start(project):
    if project.platform == "armv7-android":
        call(["adb", "shell", "am", "start", "-n", "{}/com.dynamo.android.DefoldActivity".format(project.android_id)])
    else:
        logging.error("Starting app not supported for iOS")
        sys.exit(-1)


def bob(project, options):
    if options.update:
        latest = requests.get("http://d.defold.com/stable/info.json").json()["sha1"]
        _bob.update(project, latest, options.force)

    elif options.set:
        sha = options.set
        if len(sha.split(".")) == 3:
            sha = _bob.get_sha_from_version(sha)
            _bob.update(project, sha, options.force)
    else:
        if not project.bob:
            logging.error("Can't find a bob version, download with 'builder bob --update'")
            sys.exit(1)
        sha = project.bob.split("bob_")[-1].split(".jar")[0]
        version = _bob.get_version_from_sha(sha)
        logging.info("Using version '{}', sha1: {}\n".format(version, sha))


def listen(project):
    if project.platform == "armv7-android":
        call(["adb", "logcat", "-s", "defold"])
    else:
        logging.error("Listening on log not supported for iOS")
        sys.exit(-1)


def update():
    logging.info("Updating builder")
    command = "git --work-tree={0} --git-dir=/{0}/.git pull origin master".format(os.path.dirname(__file__)).split()
    call(command)


def resolve(project):
    if project.skip_auth:
        user, pw = "", ""  # TODO: Add skip auth
    else:
        import getpass
        user = input("User: ")
        pw = getpass.getpass()
    command = ["java", "-jar", project.bob, "--email", user, "--auth", pw, "resolve"]

    call(command)


def config_set(project, command):
    if hasattr(project, command.key):
        setattr(project, command.key, command.value)
    else:
        logging.error("Attribute doesn't exists")
