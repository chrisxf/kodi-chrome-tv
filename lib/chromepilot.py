import xbmc
import xbmcgui
import xbmcaddon
import os.path
import subprocess

class ChromePilot:
    def __init__(self):
        self.extensions = []
        self.chromePath = ""
        self.url = ""

    def addExtension(self, path):
        self.extensions.append(path)

    def setChromePath(self, path):
        self.chromePath = path

    def setUrl(self, url):
        self.url = url

    def launch(self):
        extensions = _dedupList(self.extensions)
        chromePath = self._findChrome()

        if not chromePath:
            _showNotification("Chrome not found! Make sure chrome is installed or set custom path in settings!", 12000)
            return
        
        if not os.path.isfile(chromePath) or os.path.islink(chromePath):
            _showNotification("Invalid chrome path: " + chromePath)
            return

        addonPath = xbmcaddon.Addon("script.module.chrome-pilot").getAddonInfo("path")
        pilotPath = os.path.join(addonPath, "bin", "kodi-chrome-pilot")

        if not os.path.isfile(pilotPath) or os.path.islink(pilotPath):
            _showNotification("Invalid pilot path: ")
            return

        if not self.url:
            _showNotification("Browser URL not defined!")
            return

        pilotArgs = ["--chrome-path", chromePath, "--url", self.url]

        for extension in extensions:
            if os.path.isdir(extension):
                pilotArgs.append("--ext-path")
                pilotArgs.append(extension)

        xbmc.log("Chrome-Pilot: Starting with args: " + ",".join(pilotArgs), level=xbmc.LOGNOTICE)
        _runDaemon(pilotPath + " " + " ".join(pilotArgs))

    def _findChrome(self):
        chromePath = self.chromePath

        if not chromePath:
            chromePath = _runCmd("which", "chrome")
        
        if not chromePath:
            chromePath = _runCmd("which", "chromium")

        return chromePath

def _showNotification(body, time = 5000):
    title = xbmcaddon.Addon().getAddonInfo("name")
    icon = "DefaultIconError.png"

    xbmc.log("Chrome-Pilot: " + body, level=xbmc.LOGNOTICE)
    xbmc.executebuiltin('Notification(' + title + ',' + body + ',' + str(time) + ',' + icon + ')')

def _dedupList(l):
    return list(set(l))

def _runCmd(*args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]

    if proc.returncode == 0:
        return stdout
    else:
        return False

def _runDaemon(cmd):
    tmp = xbmc.translatePath('special://temp')
    service = "chrome-pilot.service"
    servicePath = os.path.join(tmp, "chrome-pilot.service")

    sf = open(servicePath, "w")
    sf.write("[Unit]\nDescription=Chrome-Pilot\n\n[Service]\nType=simple\nExecStart=" + cmd + "\n\n")
    sf.close()

    cmd = "systemctl link " + servicePath + " && systemctl start " + service + " && systemctl disable " + service
    _runCmd("sh", "-c", cmd)
