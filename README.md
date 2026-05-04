# TomoPainter
Python Script to paint images into Tomodatchi Life Living the Dream using a Raspberry Pi 4 connected to a Raspberry Pico
running [gp2040-ce](https://gp2040-ce.info) and JSON files from [Living the Grid](https://living-the-grid.com).
<!-- TOC -->
* [TomoPainter](#tomopainter)
  * [Installation](#installation)
  * [Usage](#usage)
<!-- TOC -->
## Installation
What you need:
- Raspberry Pi 4
- Raspberry Pi Pico
- 14 F2F Jumper Cables

Downlaod This Repo and the Pico version of [gp2040-ce](https://gp2040-ce.info). Install gp2040-ce on the Pico and insert
TomoPainter.py aswell the gp2040pico package in a folder of your Raspberry Pi 4.

Wire the Raspberry Pi 4 to the Pico like shown in the image below:

<img height="375" src="documentation/images/Wiring TomoPainter.png" width="381"/>

## Usage

Connect the Pi 4 to Power and the Pico to your Switch, then open [Living the Grid](https://living-the-grid.com) and export
your Image as JSON. access the Console of your Pi 4 and run the Script with you're desired file as a Parameter.

```console
python TomoPainter.py your_file_name.json
```

