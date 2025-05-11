
# Raspberry Pi Status Light

See blog post (coming soon!)


## light - LED Control Server

This is the application that runs on the Raspberry Pi and controls the lights based on a simple API call. I deploy this to my Raspberry Pi through [Balena](https://www.balena.io/) for ease of management and updates.

## cli - Mac Webcam detection CLI


This part runs on my laptop and detects when the webcam is in use through monitoring the system log - if a change in state is detected, it then sends an API call to the Raspberry Pi to switch the light on or off as appropriate.

The IP of the Raspberry Pi is set using the LED_SERVER_HOST environment variable and the colour is set through the CLI parameters e.g. `ledcli -r 255 -g 100 -b 50`