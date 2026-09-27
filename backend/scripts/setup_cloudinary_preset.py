"""One-time setup: create the unsigned Cloudinary upload preset for EKITI@30.

!! RUN THIS LOCALLY, BY HAND, ONCE. It uses the real Cloudinary API secret.
!! It is not part of the app, is never run automatically, and must never run
!! in CI or a deployed environment.

Reads CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET from
environment variables (set them in your terminal session only — never in a
committed file). Usage, from backend/:

    python scripts/setup_cloudinary_preset.py              # create the preset
    python scripts/setup_cloudinary_preset.py --dry-run    # print settings only

Then set CLOUDINARY_CLOUD_NAME and CLOUDINARY_UPLOAD_PRESET (the preset name
printed below — neither is secret) in the backend's environment.

What the preset does and doesn't enforce (per Cloudinary's docs):
- allowed_formats IS enforced by Cloudinary for unsigned uploads.
- No folder is set on the preset. For unsigned uploads a preset value always
  wins over the value sent with the upload, so setting one here would force
  every upload into that single folder. Leaving it unset lets the frontend
  pass the per-upload folder returned by POST /api/uploads/init. Cloudinary
  has no way to restrict an unsigned preset to a list of folders.
- Presets can't enforce a max file size; the frontend must check
  MAX_UPLOAD_BYTES (app/services/cloudinary_convention.py) before uploading.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cloudinary_convention import ALLOWED_FORMATS  # noqa: E402

DEFAULT_PRESET_NAME = "ekiti30_member_unsigned"


def preset_settings(name: str) -> dict[str, str]:
    return {
        "name": name,
        "unsigned": "true",
        "allowed_formats": ",".join(ALLOWED_FORMATS),
        # Cloudinary picks a random public_id; members can't choose one.
        "disallow_public_id": "true",
        "unique_filename": "true",
        "overwrite": "false",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", default=DEFAULT_PRESET_NAME, help="preset name")
    parser.add_argument(
        "--dry-run", action="store_true", help="print the settings without calling Cloudinary"
    )
    args = parser.parse_args()

    settings = preset_settings(args.name)
    print("Preset settings:")
    for key, value in settings.items():
        print(f"  {key} = {value}")

    if args.dry_run:
        return 0

    missing = [
        var
        for var in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET")
        if not os.environ.get(var)
    ]
    if missing:
        print(f"Missing environment variable(s): {', '.join(missing)}", file=sys.stderr)
        return 1

    cloud_name = os.environ["CLOUDINARY_CLOUD_NAME"]
    credentials = f"{os.environ['CLOUDINARY_API_KEY']}:{os.environ['CLOUDINARY_API_SECRET']}"

    request = urllib.request.Request(
        f"https://api.cloudinary.com/v1_1/{cloud_name}/upload_presets",
        data=urllib.parse.urlencode(settings).encode(),
        headers={"Authorization": "Basic " + base64.b64encode(credentials.encode()).decode()},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
    except urllib.error.HTTPError as err:
        # Cloudinary's error body names the problem (e.g. preset already
        # exists) and never echoes the credentials.
        print(f"Cloudinary returned HTTP {err.code}: {err.read().decode()}", file=sys.stderr)
        return 1

    print(f"\nCreated: {result}")
    print(f"\nSet CLOUDINARY_UPLOAD_PRESET={args.name} in the backend environment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
