# ThinkPad T470s UEFI Unlock

This is a thorough step-by-step guide for removing this laptop's UEFI password. It requires
some Linux knowledge and (in case you cannot boot to an OS) a partial disassembly of your laptop to get to the
chip that needs to be flashed.

## Disclaimer

I do not take any responsibility for the damage that may be caused to your device.
Doing this will void your laptop's warranty.

### Tools

If you cannot boot to the OS, you will need these tools:

- Raspberry Pi (tested with Pi 4)
  - You may opt for using a chip programmer and connecting it to another working computer
  - You may be able to use another board with GPIO pins, however the pinout may (and most likely WILL) differ from the one below. There also may be another software steps required for Flashrom to recognize the chip. So please do your own research.
- SOIC-8 clip reader (your mileage may vary)
  - You will need this to connect the EEPROM chip to the Pi in order to read it's content, patch it and write the patched content back.
  - From my research I've read people say that it is unreliable and you should desolder the chip instead, however I've had no issues with using the clip reader.
- 6 F2F jumper wires
  - These are required to connect the clip to the GPIO pins of the Pi.
- Screw driver
  - You will need it to open the device - a standard #000 Phillips screw driver is enough to do the job, you probably have one laying around.
- Time
  - This took me around 30-50 minutes to do give or take, however it may take longer depending on your skills and luck.

## 1. Setting up the Raspberry Pi

I recommend using Ubuntu as an OS. Do not try this on Windows, for the love of god please.

### 1.1 Flashrom

You will need to install `flashrom`. You can do so using the following command:

```
sudo apt-get install flashrom
```

You will also need to enable these modules:

```
sudo modprobe spi_bcm2708
sudo modprobe spidev
```

### 1.2 Working directory

Let's create a folder where we will store all related data. I'm including this part mostly for the sake of making this guide more clear.

It does not matter where or how you name the folder, however this guide will use `/home/ubuntu/t470s` for all related files, so if you use a different folder, please make sure to use the correct paths.

```
mkdir /home/ubuntu/t470s
```

### 1.3 Autopatcher

We will also need to download the autopatcher script, which patches the content of the chip to be able to remove the password. It is located in this repository (lenovo_autopatcher_0.2.zip), however that's only in case the Badcaps thread ever disappears. I strongly recommended downloading from the original thread here: https://www.badcaps.net/forum/showthread.php?t=87588&highlight=t470s

Extract the zip using `unzip` (you may need to install it using `apt-get install unzip`):

```sh
unzip lenovo_autopatcher_0.2.zip
```

This will extract a folder `lenovo_autopatcher` which we will need later.

### 1.4 Python

The script is written in Python and therefore requires the Python interpreter:

```sh
sudo apt-get install python3 python-is-python3
```

### 1.5 UEFIReplace

The autopatcher script requires `UEFIReplace`, which is part of the package `uefitool-cli`. While the zip does contain it's own UEFIReplace binary, it will not work for the RPi as it's compiled for x86 CPUs and RPi is ARM-based.

Even if you are running on a x86-based device, I still recommended doing this.

This command will install the `uefitool-cli` package:

```
sudo apt-get install uefitool-cli
```

The UEFIReplace binary we are looking for should be in `/usr/bin/UEFIReplace`, to check that, run:

```
/usr/bin/UEFIReplace
```

That should output the following:

```
UEFIReplace 0.27.0 - UEFI image file replacement utility

Usage: UEFIReplace image_file guid section_type contents_file [-o output] [-all] [-asis]
```

You'll need to remove the original binary that was extracted in the zip and link the newly installed one. To do that, run these commands:

```
rm /home/ubuntu/t470s/lenovo_autopatcher/UEFIReplace
ln -s /usr/bin/UEFIReplace /home/ubuntu/t470s/lenovo_autopatcher/UEFIReplace
```

### 1.6 Dump script

I've written a small script in this repository to dump the current content of the chip. It dumps the content 3 times to ensure the content is the same and therefore is being read correctly.

To download the script, run these commands:

```
cd /home/ubuntu/t470s
curl -O https://raw.githubusercontent.com/VottusCode/t470s-uefi-unlock/main/dump.py
```

## 2. Opening the ThinkPad

Make sure to turn off your ThinkPad. Disconnect all cables and after that proceed.

### 2.1 Unscrew the back screws

Turn the laptop around and use the Phillips screw driver to unscrew all screws. They will most likely stay in place,
they are made to not fall out.

<img src="https://i.imgur.com/Mw5Stoi.png" style="width: 500px"/>

### 2.1 Disconnecting the batteries

First, you will need to unscrew three screws holding the battery. The battery is then free and you can lift it up.

<img src="https://i.imgur.com/EQSQDar.png" style="width: 500px"/>

<img src="https://i.imgur.com/cu9kNuE.png" style="width: 500px">

You will also need to disconnect the CMOS battery. Luckily, it's just disconnecting one small cable.

<img src="https://i.imgur.com/jwu8TXL.png" style="width: 500px">

## Meet the culprit - EEPROM chip

This is the chip that will need to be flashed - right under the SSD.

<img src="https://i.imgur.com/HGDJdw9.png" style="width: 500px"/>

It might be hidden under some plastic - you can take it off, but don't throw it out and put it back later.
It's sticky so it should hold in there. If it doesn't, that's okay, it's not important and you can leave it out.

<img src="https://i.imgur.com/u1CCE4G.png" style="width: 500px"/>

## 3. Wiring up

First, let's take a look at our chip - in my case, it's a `Winbond 25Q128JVSQ`. It may be hard to read the name from the chip. Using your phone's flashlight usually helps, you can use a magnifying glass as well. If the chip model is different, it's most likely still okay, however you will need to search for the chip's datasheet / pinout (eg. google: brand model datasheet).

This is the datasheet for the chip mentioned above - https://pdf1.alldatasheet.com/datasheet-pdf/view/1243793/WINBOND/W25Q128JVSIQ.html - we are more interested in the 6th page - "Pin Configuration SOIC 208-mil".

Look at the chip on the board - there should be a dot in the corner.

<img src="https://i.imgur.com/8T2LIKJ.png" style="width: 500px">

Now look at the clip reader - there is one red line (could be a different color) on the cable - this line has to be aligned with the dot.

<img src="https://i.imgur.com/ZEQcxbX.png" style="width: 500px" />

### Connecting to Raspberry Pi

Now, connect the clip reader to the adapter board that came with it. Look at the Pin Configuration - there should be a dot next to a pin number - the adapter board also has numbers. The red line has to be aligned with the pin number of the pin with the dot next to it.

From the other side of the adapter board, connect the jumper wires to all pins except 3 and 7 - these are not used (if your chip is different, it may be different pins - check the datasheet and look for pins with fucntions "Hold or Reset Input" and "Write Protect Input").

<img src="https://i.imgur.com/veclVXz.png" style="width: 500px">

Now, let's connect the jumper wires to the Pi's pins.

This table is made for RPi 4. All previous RPi's with 40 pins should work as well (B+ and higher). If you are using a different board, you will have to find a pinout for the specific board, connect the chip's pin to the corresponding GPIO Pin.

| Pin # | SPI Pin Name  | SPI Pin Function    | RPi GPIO Pin |  RPi Pin Function  |
| :---: | :-----------: | :------------------ | :----------: | :----------------: |
|   1   |      CS       | Chip Select         |      24      | GPIO08(SPI0_CE0_N) |
|   2   |   MISO (DO)   | Data Output         |      21      | GPIO09(SP10_MISO)  |
|   3   |      WP       | Write Protect Input |  _not used_  |     _not used_     |
|   4   |      GND      | Ground              |      25      |       Ground       |
|   5   |   MOSI (DI)   | Data Input          |      19      | GPIO10(SP10_MOSI)  |
|   6   |    CLK/SCK    | Serial Clock        |      23      | GPIO11(SP10_SCLK)  |
|   7   | HOLD or RESET | Hold or Reset Input |  _not used_  |     _not used_     |
|   8   |   3.3V/VCC    | Power               |      17      |     3.3V Power     |

## 4. Dumping the chip's content

Now, we can power on the Pi. Once it booted up, go back into our working directory and run the dump script.

```
cd /home/ubuntu/t470s
sudo python3 dump.py stock
```

This will take a bit of time. If the script ends successfully with output "ok", we are ready to continue. Otherwise, the script has failed. In that case, power off the Pi, disconnect it from power, then check if you correctly connected the clip reader pins to the board, try to remove the clip from the chip and then put it on the chip again. If you fail continuously, you cannot continue. Feel free to open an issue, however you may end up with a dead end.

## 5. Patching the dump

Now that we successfully dumped the contents of the chip, we can use the autopatcher to create a patched dump.

```
cd /home/ubuntu/t470s/lenovo_autopatcher
./autopatcher.sh ../stock/stock1.rom
```

## 6. Flashing the patched dump

We can now proceed to write the patched content to the chip:

```
cd /home/ubuntu/t470s/lenovo_autopatcher
sudo flashrom -p linux_spi:dev=/dev/spidev0.0 -w stock1_PATCHED.rom
```

You should get the following output:

```
Reading old flash chip contents... done.
Erasing and writing flash chip... Erase/write done.
Verifying flash... VERIFIED.
```

After that, you can shutdown the Pi, disconnect it from the power and take the clip reader off the chip (don't disconnect it from the Pi, you will need it later to flash the stock).

## 7. Booting up

Now, boot up the device... it might take a bit longer, might reboot few times...

You will see the Lenovo logo, then you'll get few beeps and errors. Press `F1` to go to the BIOS.
It will prompt you for a password, enter any character and press enter. Next, you will see the device's Hardware ID and it will ask you to "Enter key". Just press Enter. It will then ask you to press Space bar two times. Do as it says. After that, turn off the machine. Disconnect it from power (if you have connected back the batteries, disconnect them again), connect the clip reader again and power up the Pi again.

## 8. Flashing back the stock dump

Now we need to flash the original contents of the chip back on it. Before we do that, let's check that the chip is readable.

```
cd /home/ubuntu/t470s
sudo python3 dump.py patched
```

If you fail to read the chip, refer to diagnostics above.

Now, let's flash the original content back:

```
sudo flashrom -p linux_spi:dev=/dev/spidev0.0 -w /home/ubuntu/t470s/stock/stock1.rom
```

## 9. Moment of truth

After that, shutdown the Pi, disconnect it from power, take off the clip reader and assemble your machine again. You should be able to boot the device up with no password.

## Sources

- https://github.com/bibanon/Coreboot-ThinkPads/wiki/Hardware-Flashing-with-Raspberry-Pi#reading-the-flashchip
- https://html.alldatasheet.com/html-pdf/1243793/WINBOND/W25Q128JVSIQ/2117/6/W25Q128JVSIQ.html
- https://www.badcaps.net/forum/showthread.php?t=87588&highlight=t470s

## Credits

When I initially started researching how to remove the supervisor password, I had no idea where to look. Thanks to my friends,
I've been lead to the Badcaps forum where I've managed to find the Autopatcher script. Credit is also due to @terrymeow, to whom the laptop
belongs and who helped me with going through the process and borrowed me her Raspberry Pi.

<hr>

2022 &ndash; Guide by Mia Lilian Morningstar
