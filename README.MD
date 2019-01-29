# OrangeAssist

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

```
val orangeassistPostURL = "http://lucky:charms@orangeassist:5000/assist/ask?html=1"
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

![image|243x500](https://github.com/LuckyMallari/orange-assist/blob/master/_images/homeScreenshot.png?raw=true) 

As far as creating the binding. I'm not too keen on doing it just yet. Google Assistant SDK is not that mature yet, and still keeps changing. 

Dont mind the blocky gradient (it's a gif with limited colors)
![ohbridge|690x491](https://github.com/LuckyMallari/orange-assist/blob/master/_images/HabPanelDemo.gif?raw=true)

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
3. [Clone the repo](https://github.com/LuckyMallari/orange-assist)
4. I advise that you create a virtual environment for this.
    1. Follow [VENV Instructions](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/) if you have not created a virtual environment before.
    2. Activate the environment.
5. Install the required librabries:
    ```pip install -r requirements.txt```
6. Assuming you have configured everything, you need create the credentials file:
    1. Follow instructions from [this Google page](https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials)
6. Run the code!
    ```python -m or```
6. Open helpers/tester.html

      
### Device Registration
If you have done the above, this will only allow your server to interact with Google Assistant SDK. If you actually want your assistant to show up under the 
Google Home app, you have **[REGISTER](https://developers.google.com/assistant/sdk/reference/device-registration/device-tool)** your device.


## Notes
1. This is written under Python 3.7. If there is a need for a lower version, I am willing to help and refactor.

## Empty responses
1. Google Assistant sometimes return an empty response depending on the query. In some cases, the response is empty but Audio is played on the device. Try different
[screen_modes](https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha2#google.assistant.embedded.v1alpha2.ScreenOutConfig.ScreenMode) to see which best suits your query. This is a [known issue](https://github.com/googlesamples/assistant-sdk-python/issues/158) which currently does not have a fix.

## REST API

#### Request
    1. Send a POST request to the your server instance: http://< yourserver > : < port > / assist/ask.
    2. Body of the request includes the following:
    
| Key | Required | Description |
|-----|:--------:|-------------|
| request | Yes | The actual query. You don't need to include "Okay, Google"
| uuid | No | If you include this, the response will echo it back to you.
| output_html_file | No | Where to write the response data
| output_audio_file | No | Where to write the audio data
| is_play_audio | No | If true, this will actually play the audio on the machine's default speaker
| screen_mode | No | Valid values from [here](https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha2#google.assistant.embedded.v1alpha2.ScreenOutConfig.ScreenMode)
| language | No | Valid calues from [here](https://developers.google.com/assistant/sdk/reference/rpc/languages)
| is_return_html | No | If true, the response JSON will have the complete html in the html field 

Sample Request:
```
{
    "request": "What time is it",
    "uuid": 12123e23422123,
    "output_html_file": someoutput.html,
    "output_audio_file": someaudio.wav,
    "is_play_audio": true,
    "screen_mode": "OFF",
    "language": "en-US",
    "is_return_html": true
}
```
#### Response

| Key | Description |
|-----|------------|
| request | The actual query echoed back.
| uuid | UUID echoed back.
| output_html_file | Where it saved the html
| output_audio_file | Where it saved the audio data
| html | Contains the full html code if any.

Sample Response:
```
{
    "output_audio_file": "/output/output.wav",
    "output_html_file": "/output/output.html",
    "request": "What time is it",
    "text": "It's 5:39.",
    "uuid": "9303483171002469"
}
```

#### Configuration

Configuration is done on the config.json file

| Key | Description |
|-----|------------|
is_debug | If true, you enter a console-based loop.
is_verbose | Logging level
host | Host for the server
port | Port for the server
username | If you set this with the password, a Basic Auth is enabled for the POST of the REST API. Leave blank to disable
password | If you set this with the password, a Basic Auth is enabled for the POST of the REST API. Leave blank to disable
device_model_id | [The device model ID](https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device)
device_id | [The device ID](https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device)
on_success_post_to | Not yet implemented
credentials_file | Path to your credentials file.
delete_output_files_sec | Files are kept for this number of seconds. After that, files are deleted.
screen_mode | Valid values from [here](https://developers.google.com/assistant/sdk/reference/rpc/google.assistant.embedded.v1alpha2#google.assistant.embedded.v1alpha2.ScreenOutConfig.ScreenMode)
project_id | Your Project ID

Sample Config
```
{
    "is_debug": false,
    "is_verbose": true,
    "host": "0.0.0.0",
    "port": "2828",
    "username": "lucky",
    "password": "charms",
    "device_model_id" : "XXX",
    "device_id" : "XXX",
    "on_success_post_to": "http://url_to/post_to",
    "credentials_file": "credentials.json",
    "delete_output_files_sec": 60,
    "screen_mode": "PLAYING",
    "project_id": "XXX"
}
```

### DEMO

**CLI
Set is_debug in config.json to true
![](https://github.com/LuckyMallari/orange-assist/blob/master/_images/cli.gif?raw=true)

**Tester
Set is_debug in config.json to false, then use tester.html
![](https://github.com/LuckyMallari/orange-assist/blob/master/_images/orangeAssistHtmlDemo.gif?raw=true)