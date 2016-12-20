# iBrew: The Dream Tea!

iKettle, [iKettle 2.0](http://smarter.am/ikettle) and [Smarter Coffee](http://smarter.am/coffee) Interface

## Needed remote access to iKettle 1, to test new code!

To test and finish: 
  * iKettle Emulation (emulates an iKettle with an iKettle 2.0)
  * iKettle Brigde (connect to an iKettle and use it if it was an iKettle 2.0)
  * Figure out to correct responses
  
Such that all features of iBrew are available (if supported) for the original iKettle!

So if you have an original iKettle filled up with water! And some time to spare!

Contact <tristan@monkeycat.nl>!


## Downloads
  * [Windows](https://dl.dropboxusercontent.com/u/12474226/iBrew.exe)
  * [MacOS]  (https://dl.dropboxusercontent.com/u/12474226/iBrew.dmg)
  * [Source] (https://github.com/Tristan79/iBrew/archive/master.zip)

## Hot! News

Now! macOS & windows apps! With nice icon in the taskbar! :-)

__Trigger! You can now push your data or run commands!__
It is now possible to push sensor values and states of the appliances to other smarthome controllers using HTTP or run commands!

__Please post links, information or help on interfacing with smarthome controllers software in the issues! There are too many out there for me to test and write guides for them all!__.
If you are a plugin coder or scripter and you do not have an iKettle or Smarter Coffee, __just simulate one!__

* Simulates iKettle 2.0 ```ibrew simulate```
* Simulates Smarter Coffee machine ```ibrew simulate```


## Introduction
iBrew is an interface to the iKettle 2.0 and Smarter Coffee devices (and has legacy support for the original iKettle, see below). 

_Stand alone, no internet or Smarter app needed!_

It features! 

__For smarthome fans!__
 * Support unlimited iKettle 2.0 or Smarter Coffee appliances! As many as you like!
 * Usage statistics!
 * No tracking!
 * Stand alone or bridge mode!
 * HomeKit Support
 * HTTP push!
 
__iBrew Interfaces & Bridges__
 * Command Line (now with iKettle Legacy support) 
 * Web (almost finished, help appreciated!)
 * JSON REST 
 * [Javascript](https://github.com/Tristan79/iBrew/blob/master/resources/ibrew.js) (almost finished :-)
 * [Python 2.7] (https://github.com/Tristan79/iBrew/tree/master/smarter) 
 * Message relay (works with Smarter app!)
 
__Connection Guides__
 * __HomeKit__ (using HomeBridge)  
 * [Domoticz](http://www.domoticz.com/) 
 * [Home Assistant](https://home-assistant.io)
 * [OpenHAB](http://www.openhab.org) 
 * [Smartthings](https://www.smartthings.com)
 * Improve your connection with a relay server 
 * Please share your favorite smarthome controller setup!

_No tracking of you or your appliances usage!_
 
__For the Smarthome and Domotics Interface experts!__
 * Kettle and coffee machine simulation (works with Smarter app!)
 * Console for Smarter protocol debugging
 * Monitor
 * Message blocking and patching
 * Smarter protocol description (start web interface for a clickable web version :-)

Tested on iKettle 2.0 v19 and SmarterCoffee v20 & v22. 

<tristan@monkeycat.nl>

Please share any bugs, jokes, problems, discoveries you made! 

### Legacy support of the original iKettle 

It features! 

__For smarthome fans!__
 * Command Line
 * HomeKit support 
 * Relay
 * Simulator

#### Usefull links
Check out [ikettle-brute-forcer](https://github.com/C0smos/ikettle-brute-forcer)
        
### iBrew in the Media
[The iKettle, the Eleven-Hour Struggle to Make a Cup of Tea, and Why It Was All About Data, Analytics and Connecting Things Together](https://medium.com/mark-rittman/the-story-behind-the-ikettle-the-eleven-hour-struggle-to-make-a-cup-of-tea-and-why-it-was-all-769144d12d7#.h62foolse) 


### Old :-) News
I would like to thank Ju4ia for letting me access his coffee machine remotely, and get more Smarter Coffee missing protocol bits, and... that I could test the client code. And all the other people helping track down bugs and supplying new features, whether by e-mail or in the issues, Thanks!

Since the console it nearly done, protocol almost fully mapped out. It is time to focus on the webpage... the framework is working, it auto reconnect, keeps some stats and you can even preform some actions with it.


## Contact
[Bugs or issues](https://github.com/Tristan79/iBrew/issues). 

<tristan@monkeycat.nl>

If you have jokes on coffee, tea, hot chocolade, coffee machines or kettles, please post in the issues!

### Other stuff 

[iSamsungTV](https://github.com/Tristan79/iSamsungTV) the command line interface to Samsung TV series C, D, E, F and Blue Ray Disc Players with Smart Hub feature.

 
## Installing

Other systems than Windows, MacOS or Pi that are running python see download from source section.

### Windows 

  * [Windows]  (https://dl.dropboxusercontent.com/u/12474226/iBrew.exe)

#### From source
First no python is installed by default so head up over to [python](https://www.python.org/downloads/) and install v2.7 (NOT 3)
Secondly you need [make](http://gnuwin32.sourceforge.net/packages/make.htm) and the python [win32 package](https://sourceforge.net/projects/pywin32/files/pywin32/)

Use `make setupwin` to setup
Use `make win` to create a package 
Use `make cleanwin` to clean up

### MacOS
  * [MacOS]  (https://dl.dropboxusercontent.com/u/12474226/iBrew.dmg)

Once you start the app from the MacOS package (drag it to your application folder first) it will auto link iBrew in your terminal.
Open a terminal and run ```ibrew``` and you're all set, good to go!

_it creates a soft symlink to /usr/local/bin/ibrew,... :-)_

#### From source
Make sure either the command line or xcode is installed, just run `make` and it will promt for a download!

Use `make setupmac` to setup
Use `make mac` to create a package 
Use `make cleanmac` to clean up

### Linux

See Pi section.

### Source

You can run iBrew on systems that run python 2.7. Download and unpack the [source](https://github.com/Tristan79/iBrew/archive/master.zip), download it from github using [Github Desktop](https://desktop.github.com) or manually `git clone https://github.com/Tristan79/iBrew.git`. Finish the setup with running `make setup` in the iBrew folder to configure the python packages for bare bones operation. Update to the latest version of iBrew with `git pull`. Run `make` to see all other options possible.

#### Bonjour

Bonjour is not enabled by default, to install it use `make bonjour` or for windows `make bonjourwin`. But you have to have bonjour installed on your system, macOS its out of the box, on most linux system you can install it with (or try equivalent packages for your *nix distro) `apt-get install avahi-daemon avahi-discover libnss-mdns` and on Windows you either install iTunes or download it from [apple](http://developer.apple.com/networking/bonjour/download/)
Also check out [pybonjour](https://code.google.com/archive/p/pybonjour/)

### Raspberry Pi Jessy (light)

Tested on a clean Jessy light image (september 2016). 

Use `make setuplin` to setup
Use `make cleanlin` to clean up

#### Install 

SSH to the Pi! And use:

```
cd ~
sudo apt-get install git
sudo apt-get install python-setuptools
sudo easy_install pip
git clone https://github.com/Tristan79/iBrew.git
cd ~/iBrew
sudo make setuplin
sudo ln -s ~/iBrew/ibrew /usr/local/bin/ibrew
```

Now you can start ibrew from anywhere :-) Type in your terminal

```
ibrew
```

Or if you want to start the web interface with event triggers type 

```
ibrew events web
```

And surf to your pi on port 2080!

#### Update 

You can update to the latest version of iBrew with

```
cd ~/iBrew
git pull
```

#### Start web server on pi boot

To add the webserver on boot run

```
sudo nano /lib/systemd/system/iBrew.service
```

Copy and paste this text and save with ctrl-x

```
[Unit]
Description=iBrew
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/iBrew/ibrew events web
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

Then run the additional commands
```
sudo chmod 644 /lib/systemd/system/iBrew.service
sudo systemctl daemon-reload
sudo systemctl enable iBrew.service
sudo systemctl start iBrew.service
sudo systemctl status iBrew.service
```

#### Troubleshooting

Please post any bug or [issues](https://github.com/Tristan79/iBrew/issues) here on github!
The error handling is still kinda broken... :-) now use dump to see more. Will revert to debug, info, logging (wip)

### Log & config location

#### Log 
 * macOS ```~/Library/Application Support/iBrew/logs```
 * unix  ```~/.iBrew/logs```
 * unix (root) ```/var/log/iBrew/```
 * windows ```~%APPDATA%\iBrew\logs```
 
#### Config
 * macOS ```~/Library/Application Support/iBrew/```
 * unix  ```~/.iBrew/```
 * unix (root) ```/etc/iBrew/```
 * windows ```~%APPDATA%\iBrew\logs```
 

### Unable to connect to iKettle 2.0 or Smarter Coffee appliance

```
MoonTwo:iBrew Tristan$ ./ibrew list
[10.0.0.3:2016-11-13 12:38:24] Found iKettle 2.0 (iBrew certified firmware v19)
[10.0.0.98:2016-11-13 12:38:24] Found Smarter Coffee (iBrew certified firmware v20)
[10.0.0.99:2016-11-13 12:38:24] Found iKettle 2.0 (iBrew certified firmware v19)
```
Some hints
* Did you download, clone or pull iBrew from git to get the latest version with all the bug fixes?

Network trouble
 * Does the Smarter app autodetects it?
 * Is a firewall blocking port 2081 on your computer (or on your router)?
 * Does ```./ibrew list``` work?
 * Make sure that your kettle/coffee machine is on the same network and subnet as your pc and your phone.
 * It could be that your router is blocking utp broadcast messages (some do, so it never auto detects). 
 * Running it on a computer with only a loopback device will result in auto detection be disabled (when using the simulator)

Static IP address
 * Look up the IP address of the appliance in your router (dhpc server)
 * Set up a static IP address in your router (dhpc server) for your appliance

Reset wireless network
 * Reset appliance (iKettle is longer then 10 seconds button hold on base, coffee machine, eeuh I forgot which button but you can use the smarter app to reset your appliance wireless network to direct mode [FIX])
 * If the appliance is reset. Try connect with your wifi of your pc (if it has wifi) to the appliance its wireless network access point iKettle:?? or SmarterCoffee:?? try if iBrew works.
 * Reconnect to your wifi network (and if you are lucky and could connect with iBrew in direct mode, the command is ./ibrew join namewireless password) else use your phone app.



## Usage

### Command Line

See the console section for the commands.
 
```
