# mixy-dfu
A tool for updating firmware of Mixy devices.

It can also work with other targets with UF2 bootloader, 
if they support resetting via magic baudrate setting (like RPi Pico).

## Requirements

- **Python >= 3.10**
- **pyserial**
- pywin32 (optional, used for UF2 auto upload on Windows)

## How to use

Only reset with `python3 -m mixy_dfu`
Reset and UF2 upload with `python3 -m mixy_dfu --firmware file.uf2`

If you installed the package then `python3 -m mixy_dfu` can be replaced with just `mixy_dfu`


## Alternative tool

If you really need this sweet memory safety or above requirements are too high for you,
there ~~is~~ will be an alternative in form of a blazingly fast Rust version of mixy-dfu.

> [!WARNING]
> WORK IN PROGRESS