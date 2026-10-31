
import csv
import qrcode
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "data" / "names.csv"
OUTPUT_DIR = BASE_DIR / "qr_codes"

# Local testing URL
BASE_URL = "http://innovatorsconclave.org.in/verify"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for participant in reader:
            username = participant["username"].strip()
            credential_id = participant["credential_id"].strip()

            if not credential_id:
                print(f"Skipping {username}: missing credential ID")
                continue

            verification_url = f"{BASE_URL}/{credential_id}"

            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )

            qr.add_data(verification_url)
            qr.make(fit=True)

            image = qr.make_image(
                fill_color="black",
                back_color="white"
            )

            output_path = OUTPUT_DIR / f"{credential_id}.png"
            image.save(output_path)

            print(f"Generated QR: {credential_id}")

    print(f"\nQR generation completed: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
