# DefBuild
Builder is built by wrapping adb/idevicebuilder and storing some data locally.

## But why?

DefBuild enables you to easily build, install, uninstall and more for both Android and iOS with a simple unified interface.
It also enables you to build with the specific Defold version you want. If you encounter a problem with the Defold version
you are on you can easily build with an older one to see if the problem was in that version too, switching between versions
is done lie this `builder bob --set 1.2.143`.

It is very handy to uninstall, build and install from the same interface. Using DefBuild you don't need to remember all
paths, Bundle Identifications and Package names.

Instead of doing this where you have to remember all options, if they take a path or an id, which bob version you have 
downloaded and so on
```
bob java -jar /Users/jerakin/Downloads/bob.jar --archive --platform armv7-android distclean build bundle
adb uninstall com.example.todo
adb install "./build/default/My Game.apk"
```

You can instead do this and builder will figure out the paths and identifiers for you, (if you do repeated build you 
don't have to specify platform, it remembers last platform used)
```
builder build . -p android
builder install .
builder uninstall .
```


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
  build              [project location]         Project location, use . for current directory
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
                     
  config             [key, value]               See description below
  
  resolve                                       Updates the dependencies
```
  

#### Example usage
Make sure you have bob up to date

You can either update to the latest `builder bob --update`

or you can use a specific version `builder bob --set 1.2.130`

Make sure your dependencies are up to date `builder resolve`

Build the project `builder build . --platform android`, you only need to specify the project the first time or when 
switching platform.

Install the project on your connected android `builder install .` it will install a build for the project correlating to
 the current directory

You can automatically start the project with `builder start .` as well as get the logs with `builder listen .`

A nifty trick is to chain the commands so it does it all in sequential order for you 
`builder build . && builder install . -f && builder start .`

### Config
set is used for setting config values, it takes 2 arguments key and value.

If you want to install and uninstall on iPhone both 'identity' and 'provision' needs to be set.


```
Usage:
  builder config identity 'iPhone Dev: Me'
  builder config provision path/to/provision/game.mobileprovision
```
