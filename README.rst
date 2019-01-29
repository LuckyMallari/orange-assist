_**OrangeAssist**_


**What this does**:
This is basically Google Home **(GH)** Hub equivalent for HabPanel. It not only acts as a "audio-visual element," but it fully integrates to Google Assistant as if you are in front of a Google Assistant device (google home, google home mini, google home hub, etc).

We have a combination of 8 Google Devices (home, mini, hub) throughout the house and they work beautifully with openHAB **with few exceptions:**
* You have a device supported by Google Assistant/Device but not openHAB
* You have an openHAB device not supported by Google Assistant
* You want Google Assistant to control security devices, rather than openHAB

So basically, I have a few security locks that are supported by Google Home, but currently do not have an openHAB binding. I can say "Lock the front door" to GH, and it will lock it, but I can't lock them through an openhab rule. That's how/why i came up with orangeassist.

I created this with python using [Google Assistant Service since the Library version does not support text input](https://developers.google.com/assistant/sdk/overview#features) yet. I didn't want it to run in same hardware as OH yet, so it's running in a tiny orange pi on a headless armbian. This orange pi also hosts my NCID server for my [caller id + habpanel integration](https://community.openhab.org/t/how-to-integrate-your-home-phone-with-openhab/39729)

Many of us here use Chromecast Binding as audio sink for OH, but we all know that using that basically STOPS whatever is currently playing and does not resume. With this new integration, instead of using `say()` in my rules, I simply send "broadcast XXXX" to **OrangeAssist** and can even use the built in GH chain commands like "broadcast time to eat then turn on kitchen lights"

A simple rule to send the command to **OrangeAssist**.

```val orangeassistPostURL = "http://lucky:charms@orangeassist:5000/assist/ask?html=1"
val timeoutSec = 10

rule "Send OrangeAssist Command"
when
	Item orangeassistcmd received command
then
	var result = sendHttpPostRequest(orangeassistPostURL, "text/plain", orangeassistcmd.state.toString, timeoutSec*1000)
	postUpdate(orangeassistcmdResult, result)
	orangeassistcmdSwitch.sendCommand(ON)
end
```

As you may have noticed. I wrote the OrangeAssist REST API part with Basic Auth as a simple security.  Some might ask about the popup/slider. This HTML is provided by Google themselves as part of the SDK/API response.

_What I really like about this is that it opens EVERY QUERY you can think of and it will answer back, just like being in front of a Google Home device. The difference here is that you can automate those queries, and use  text as input instead of your voice._ 

Here's one of my favorites:
When I wake up (usually at 4AM), I go to the kitchen to prepare my breakfast. My security cameras (Blue Iris) detects motion and triggers OH. OH turns on the kitchen lights (zwave). After turning on the lights, OH sends **"how's my day"** to **OrangeAssist**, which then triggers a routine of my Google Home device. It tells me the weather, my appointments, how long my drive to work is, etc.

You can also REGISTER the instance and OrangeAssist will show up as a device under your Google Assistant app:

![image|243x500](upload://mFxy5nTzEKNhSRSmqifv5TybwYd.png) 

As far as creating the binding. I'm not too keen on doing it just yet. Google Assistant SDK is not that mature yet, and still keeps changing. 

Dont mind the blocky gradient (it's a gif with limited colors)
![ohbridge|690x491](upload://1nkR8QwaD7KDiPomusdpOhNrxSw.gif)

Dont worry. If I don't create the binding, I will at least create a HOW-TO.



# Orange Assistant

## Steps
1. Familiarize yourself with [Google Assistant SDK](https://developers.google.com/assistant/sdk/overview)
2. [Configure a Developer Project and Account Settings](https://developers.google.com/assistant/sdk/guides/library/python/embed/config-dev-project-and-account). The link already shows you the steps, but here they are anyway.
    1. Go to [Google Actions](https://console.actions.google.com/)
       1. If you don't have an existing project, click Add/Import
       2. If you have an exiting project, just click it
    2. [Enable Google Assistant API](https://console.developers.google.com/apis/api/embeddedassistant.googleapis.com/overview)
       1. Make sure your project is selected (drop down on top)
    3. [Configure Consent Screen](https://console.developers.google.com/apis/credentials/consent)
    4. [Configure Activity Controls](https://myaccount.google.com/activitycontrols?pli=1) **(IMPORTANT!!)** Make sure these are enabled:
        * Web & App Activity
        * Include Chrome history and activity from sites, apps, and devices that use Google services
        * Device Information
        * Voice & Audio Activity
    5. [Register your device](https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device)
        1. **REMEMBER Model Id. We will need that for later**
        2. Here's Mine:....
        
# W-I-P