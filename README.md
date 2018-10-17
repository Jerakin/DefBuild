# DefBuild
Builder is built by wrapping adb/idevicebuilder and storing some data locally.

## Getting started

You will need some dependencies, if you are on mac they are easiy installed with brew.
If you are on windows you will have to download them from their websites, please note
that you can't use the iOS installation/build capabilities on a windows machine.

#### Dependencies

[Python 3.2+](https://www.python.org/) `brew install python3`

[adb](https://developer.android.com/studio/command-line/adb) `brew install android-platform-tools`

[ideviceinstaller](http://www.libimobiledevice.org/) `brew install ideviceinstaller`

#### Install

Install it with pip `pip install defbuild`

If you prefer you can clone and build the project yourself


## Usage
Builder installs itself as a command, run it with "builder command arguments"
```
Usage:
  builder.py [command] [arguments]
 
Available Commands:
  build              [project location]         Project location specifed either a dot . or nothing
                     -p, --platform [arg]       For which platform you want to build ios/android
                     -q, --quick                Do a quickbuild by skipping distclean
                     -o, --options              Use a properties file to override or add values to the .project file
 
  install            [project location]
                     -f, --force                Forces the installation by first uninstalling the application
                     -p, --platform [arg]       For which platform you want to install on ios/android
 
  uninstall          [project location]
                     -p, --platform [arg]       For which platform you want to install on ios/android
 
  start              [project location]         THIS COMMAND IS ANDROID ONLY
 
  listen             [project location]         THIS COMMAND IS ANDROID ONLY
 
  bob                --update                   Updates bob to the latest version
                     --set [arg]                Updates bob to the specified version, takes either a sha1 or 
                                                version in format '1.2.117'
                     --force                    Forces bob to download a new bob version, used with --update or --set
                     
  set                [key, value]               See description below
  
  resolve                                       Updates the dependencies
```
  


### Set
set is used for setting config values, it takes 2 arguments key and value.

If you want to install and uninstall on iPhone both 'identity' and 'provision' needs to be set.


```
Usage:
  builder config identity 'iPhone Dev: Me'
  builder config provision path/to/provision/game.mobileprovision
```
