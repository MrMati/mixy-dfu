# mixy-dfu
A tool for updating firmware of Mixy devices.

It can also work with other targets with UF2 bootloader, 
if they support resetting via magic baudrate setting (like RPi Pico).

## Requirements

- **Python >= 3.10**
- **pyserial** (if not using pyz archive)

## How to use

By default, the tool only resets the device into bootloader mode.
Just run `python3 -m mixy_dfu` in repo, or `python3 mixy_dfu.py` if downloaded from the releases.

To reset and upload a UF2 file, use the `--firmware file.uf2` argument

If you installed the package then `python3 -m mixy_dfu` can be replaced with just `mixy_dfu`.

Releases also include a pyz archive that contains pyserial.
Just run it like a script -  `python3 mixy_dfu.pyz`. 

## Alternative tool

If you really need this sweet memory safety, or above requirements are too high for you,
there ~~is~~ will be an alternative in form of a blazingly fast Rust version of mixy-dfu.

> [!WARNING]
> WORK IN PROGRESS