#!/usr/bin/env python
"""
Builder is built by wrapping bob, adb, ideviceinstaller and storing some data locally


------------------------------------------------------------------------------------------
Installation
I would recommend to add an alias to your command line tool, that way you don't need to spell out the complete script.
Create this alias in ~/.bash_profile alias builder="python3.5 /path/to/builder/builder_android.py"


# Mac
install brew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

install python 3.2+
brew install python3

install python requests
pip install requests

install adb
brew install android-platform-tools

install ideviceinstaller
brew install ideviceinstaller



# Windows
install python
python.org

install python requests
pip install requests

install adb
goo.gl/3Rasvk

You can't use the iOS installation capabilities on a windows machine :(


------------------------------------------------------------------------------------------
Usage:
  builder.py [command] [arguments]

Available Commands:
  build      build [location of a project] [arguments]
  install    install [path to APK]
  uninstall  uninstall [bundle id]
  start      start [bundle id]
  listen     listen
  bob        bob arguments
  set        set [key, value]
  update     updates builder by pulling the latest changes from master

bob arguments:
  --update   Updates bob to the latest version
  --set      Updates bob to the specified version, takes either a sha1 or version in format '1.2.117'
  --force    Forces bob to download a new bob version, used with --update or --set


Usage with set:
  set is used for setting config values, it takes 2 arguments key and value
  If you want to install and uninstall on iPhone both 'identity' and 'provision' needs to be set.
  You can enable verbose output with 'verbose'

Usage:
  builder set identity 'iPhone Dev: Me'
  builder set provision path/to/provision/game.mobileprovision
  builder set verbose true

"""

import os
import sys
import logging
import commands


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
if not sys.version_info >= (3, 3):
    logging.error("Python version needs to be of 3.3 or higher")
    sys.exit(1)

import shutil
import configparser
import argparse

try:
    import requests
except ImportError:
    ver = sys.version_info
    logging.info("Python version is {}.{}.{}".format(ver.major, ver.minor, ver.micro))
    logging.error("requests not found, install with `pip install requests`")
    sys.exit(1)

__version__ = "1.0.0"


class Project:
    def __init__(self, arguments):
        self.arguments = arguments
        _project_path = arguments.project if hasattr(arguments, 'project') and arguments.project else "."

        self.cache_dir = os.path.join(os.path.expanduser("~"), ".builder", "cache")
        self.project_file = _get_project_file(os.path.abspath(_project_path))
        self.output = os.path.join(self.cache_dir, "output")

        self.platform = arguments.platform if hasattr(arguments, 'platform') else None
        self.report = arguments.report if hasattr(arguments, 'report') else None
        self.quick = arguments.quick if hasattr(arguments, 'quick') else None
        self.force = arguments.force if hasattr(arguments, 'force') else None
        self.name = None
        self.provision = None
        self.identity = None
        self.bob = None

        self.ios_id = None
        self.android_id = None
        self.ios_build = None
        self.android_build = None

        if hasattr(arguments, 'options') and arguments.options:
            path, name = os.path.split(self.project_file)
            shutil.copy(self.project_file, os.path.join(path, "{}_old".format(name)))

            options_file = os.path.abspath(arguments.options)
            _merge_properties(self.project_file, options_file)

        self.load()

    def load(self):
        config = self._load_config()
        game_config = _load_game_config(self.project_file)
        self.name = game_config.get("project", "title")
        self.ios_id = game_config.get("ios", "bundle_identifier", fallback="com.example.todo")
        self.android_id = game_config.get("android", "bundle_identifier", fallback="com.example.todo")

        self.bob = config.get("config", "bob", fallback=None)
        self.identity = config.get("config", "identity", fallback=None)
        self.provision = config.get("config", "provision", fallback=None)
        self.output = config.get("config", "output") if config.has_option("config", "output") else self.output

        self.platform = self.platform if self.platform else config.get("config", "platform") if config.has_option(
            "config", "platform") else None

        self.platform = "armv7-android" if self.platform in ["android", "armv7-android"] else \
            "armv7-darwin" if self.platform in ["ios", "armv7-darwin"] else None

        if not self.platform:
            logging.error("No platform found, specify ios or android")
            sys.exit(1)

        if self.name not in config.sections():
            return

        self.ios_build = config.get(self.name, "ios_build", fallback=None)
        self.android_build = config.get(self.name, "android_build", fallback=None)

    def final(self):
        # Final clean up
        if hasattr(self.arguments, 'options') and self.arguments.options:
            path, name = os.path.split(self.project_file)
            os.remove(self.project_file)
            os.rename(os.path.join(path, "{}_old".format(name)), self.project_file)

        self.save()

    def save(self):
        config = self._load_config()
        if not config.has_section(self.name):
            config.add_section(self.name)
        config.set(self.name, "ios_id", self.ios_id)
        config.set(self.name, "android_id", self.android_id)

        if self.android_build:
            config.set(self.name, "android_build", self.android_build)
        if self.ios_build:
            config.set(self.name, "ios_build", self.ios_build)
        if self.identity:
            config.set("config", "identity", self.identity)
        if self.provision:
            config.set("config", "provision", self.provision)
        config.set("config", "platform", self.platform)
        config.set("config", "bob", self.bob)
        config.set("config", "output", self.output)

        with open(os.path.join(self.cache_dir, "session"), 'w') as f:
            config.write(f)

    def _load_config(self):
        path = os.path.join(self.cache_dir, "session")
        if not os.path.exists(path):
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)

            config = configparser.RawConfigParser()
            config.add_section('config')

            with open(path, 'w') as f:
                config.write(f)

        config = configparser.ConfigParser()
        config.read(path)
        return config


def _load_game_config(project_file):
    config = configparser.ConfigParser()
    config.read(project_file)
    return config


def _get_project_file(folder):
    for x in os.listdir(folder):
        if x.endswith(".project"):
            return os.path.join(folder, x)

    logging.error("Can not find project file in this location {}".format(folder))
    sys.exit(1)


def _merge_properties(project_file, properties_file):
    project = configparser.ConfigParser()
    project.read_file(open(project_file))
    properties = configparser.ConfigParser()
    properties.read_file(open(properties_file))

    for section_name, section_proxy in properties.items():
        for name, value in properties.items(section_name):
            if not project.has_section(section_name):
                project.add_section(section_name)
            project.set(section_name, name, value)
    with open(project_file, "w") as f:
        project.write(f)


def main():
    options = init()
    project = Project(options)
    try:
        if options.command == "build":
            commands.build(project)
        elif options.command == "install":
            commands.install(project)
        elif options.command == "uninstall":
            commands.uninstall(project)
        elif options.command == "resolve":
            commands.resolve(project)
        elif options.command == "start":
            commands.start(project)
        elif options.command == "listen":
            commands.listen(project)
        elif options.command == "update":
            commands.update()
        elif options.command == "set":
            commands.config_set(project, options)
        elif options.command == "bob":
            commands.bob(project, options)
    finally:
        project.final()


def init():
    parser = argparse.ArgumentParser(description='Builder')
    sub_parsers = parser.add_subparsers(dest="command")

    sub_build = sub_parsers.add_parser("build")
    sub_build.add_argument("project", help="working directory to project")
    sub_build.add_argument("-p", "--platform", help="which platform to build, 'ios' or 'android'", dest="platform", choices=["android", "ios"])
    sub_build.add_argument("-q", "--quick", help="option to do a quick build by skipping distclean",
                           action='store_true', dest="quick")
    sub_build.add_argument("-o", "--options", help="Read options from properties file. Options specified on the "
                                                   "commandline will be given precedence over the ones read from "
                                                   "the properties file", dest="options")
    sub_build.add_argument("-r", "--report", help="which platform to build, 'ios' or 'android'", action="store_true", dest="report")

    sub_install = sub_parsers.add_parser("install")
    sub_install.add_argument("project", help="what to install", nargs="?")
    sub_install.add_argument("-f", "--force", help="force installation by uninstalling first", action='store_true', dest="force")
    sub_install.add_argument("-p", "--platform", help="which platform to install on, 'ios' or 'android'", nargs="?", dest="platform")

    sub_uninstall = sub_parsers.add_parser("uninstall")
    sub_uninstall.add_argument("project", help="which app to uninstall", nargs="?")
    sub_uninstall.add_argument("-p", "--platform", help="which platform to uninstall, 'ios' or 'android'", nargs="?", dest="platform")

    sub_parsers.add_parser("start")

    sub_parsers.add_parser("listen")

    sub_config = sub_parsers.add_parser("set")
    sub_config.add_argument("key", help="key to update")
    sub_config.add_argument("value", help="the value to assign to key")

    sub_bob = sub_parsers.add_parser("bob")
    sub_bob.add_argument("-u", "--update", help="update bob", action='store_true', dest="update")
    sub_bob.add_argument("-f", "--force", help="force download of bob", action='store_true', dest="force")
    sub_bob.add_argument("--set", help="download a specific version of bob", dest="set")

    sub_parsers.add_parser("update")

    sub_resolve = sub_parsers.add_parser("resolve")
    sub_resolve.add_argument("-s", "--skip-auth", help="skips auth by using fake credentials", action='store_true', dest="skip_auth")

    input_args = parser.parse_args()
    try:
        pass
    except AttributeError:
        logging.error("No command sent, use --help for usage")
        sys.exit(1)

    return input_args


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
    except:
        raise
