# dbus-p1
Read gasmeter from a Dutch energy meter via the P1 port, using the DSMR protocols.

DSMR is short for Dutch Smart Meter Requirements, somehow related to NTA8130.

The Python code in the repo is basically a wrapper around the
[nrocco/smeterd](https://github.com/nrocco/smeterd/) repo.

Adding the power meter readings as well will be trivial. But since my (Dutch) Smart Meter
only sends an update every 10 seconds, which is too little for proper ESS operation, I have not
bothered to implement that, yet. Apparently the (recent) DSMR 5 spec increases the update
rate to 1 Hz, which is probably sufficient for ESS.

## tested meter & cable

Above mod of the serial-starter depends for the ID_MODEL USB property to equal `P1_Converter_Cable`.
Which is (probably) the P1 Converter Cable V2 as sold here: http://www.smartmeterdashboard.nl/webshop.

I tested it on a Landis + Gyr E350 ZMF110CCtFs2 3-phase meter, with a DSMR 4.2 module.

## installation

Requires [Venus](https://github.com/victronenergy/venus/wiki) v2.12~21 or newer:
relies on [pyserial](https://github.com/victronenergy/meta-victronenergy/commit/956c404515c37d0678d52c3afc9628bf68e85a22).

See [here](https://www.victronenergy.com/live/ccgx:root_access) for how to obtain root access to Venus.

### Step 1. Install crcmod
dbus-p1 depends on crcmod (for the crc16 calculation). Find the installable ipks in the crcmod
folder. For Venus running on a raspberrypi2 take the cortexta7 file, for ccgx and beaglebone take
the cortexa8 one. Copy the file to the target and install with:

    opkg install python-crcmod_1.7-r0_cortexa7hf-vfp-vfpv4-neon.ipk

### Step 2. Install dbus-p1

Clone this repo, and its submodules(!). Copy the whole thing over to the Venus device. And run it.

FIXME: add instruction on how to make it get started at boot, or even better, add it natively to
serial-starter.

### Step 3. serial-starter mod

Modify `/opt/victronenergy/serial-starter/serial-starter.sh` line 94:
Add `P1_Converter_Cable` to the list of ignored ids. After the change that line would look like this:

```
        USB-Serial_Controller_D)
            echo cgwacs:gps
            ;;
        ignore|P1_Converter_Cable)
            echo ignore
            ;;
```

Background details
[here](https://github.com/victronenergy/venus/wiki/commandline-introduction#serial-port--serial-starter).

And instead of making serial-starter ignore the dbus-p1 script it would be even better to make it auto-
start the dbus-p1 script. Not that hard: go for it!

## dsrm info

DSMR2 & 3 meters:
- 9600 baud
- Even parity
- 7 Data bits
- 1 Stop bit
- Wel/Geen xon/xoff
- No rts/cts

DSMR 4 meter:
- 115200baud
- no parity
- 8 Data bits
- 1 Stop bit
- Preferably enable xon/xoff
- No rts/cts

[source SmartMeterDashboard.nl](http://www.smartmeterdashboard.nl/blog/p1convertercablenutebestellenindewebshop/P1CC%20Info.txt)
