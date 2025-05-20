# Public-Software-Resources Procedures

These instructions are for maintainers (Train Control Systems).

## Adding firmware files
- Clone this repo and Depot.
- Ensure you choose an encrypted image.
  - Name/rename the firmware BIN file according to naming conventions (See documentation in Google Drive):
    This is required so that Depot can match the firmware with the product.
- Use FirmwareRepoManager.py in Depot, and fill in the form.
- Be sure to stage both files (Firmware Repo Manager 1. adds your bin file, 2. changes metadata.json) on this repo, then commit and push when ready.