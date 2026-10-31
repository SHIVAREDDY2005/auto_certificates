
import csv
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ==============================
# PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "data" / "hackathon_certificate.png"
CSV_PATH = BASE_DIR / "data" / "names.csv"

OUTPUT_DIR = BASE_DIR / "certificates"


# ==============================
# CERTIFICATE NAME SETTINGS
# ==============================

NAME_CENTER_X = 295
NAME_CENTER_Y = 516

MAX_NAME_WIDTH = 400

NAME_COLOR = "#393078"

# FONT SETTINGS
FONT_PATH = BASE_DIR / "fonts" / "Montserrat-VariableFont_wght.ttf"

START_FONT_SIZE = 22
MIN_FONT_SIZE = 12


# ==============================
# FONT LOADER
# ==============================

def load_font(size):

    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Font not found: {FONT_PATH}")

    font = ImageFont.truetype(str(FONT_PATH), size)

    # Set Montserrat to Bold (weight 700)
    font.set_variation_by_name("Bold")

    return font


# ==============================
# READ CSV
# ==============================

def read_participants(csv_path: Path):

    with csv_path.open(
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames or "username" not in reader.fieldnames:
            raise ValueError(
                "CSV must contain a username column."
            )

        participants = []

        for row in reader:

            username = (row.get("username") or "").strip()
            credential_id = (row.get("credential_id") or "").strip()

            if username:
                participants.append({
                    "username": username,
                    "credential_id": credential_id
                })

    if not participants:
        raise ValueError("No participants found in CSV.")

    return participants


# ==============================
# SAFE FILE NAME
# ==============================

def safe_filename(name, index):

    cleaned = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        name.strip()
    ).strip("_")

    return f"{index:04d}_{cleaned or 'participant'}"


# ==============================
# ADD NAME TO CERTIFICATE
# ==============================

def add_name(template_path, name, output_png):

    image = Image.open(template_path).convert("RGBA")

    draw = ImageDraw.Draw(image)

    font_size = START_FONT_SIZE

    while font_size >= MIN_FONT_SIZE:

        font = load_font(font_size)

        bbox = draw.textbbox(
            (0, 0),
            name,
            font=font
        )

        text_width = bbox[2] - bbox[0]

        if text_width <= MAX_NAME_WIDTH:
            break

        font_size -= 1

    draw.text(
        (NAME_CENTER_X, NAME_CENTER_Y),
        name,
        fill=NAME_COLOR,
        font=font,
        anchor="mm"
    )

    # Save PNG
    image.save(output_png, "PNG")

    # Save PDF
    white_bg = Image.new(
        "RGB",
        image.size,
        "white"
    )

    white_bg.paste(
        image,
        mask=image.getchannel("A")
    )

    output_pdf = output_png.with_suffix(".pdf")

    white_bg.save(
        output_pdf,
        "PDF",
        resolution=96
    )


# ==============================
# MAIN FUNCTION
# ==============================

def main():

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE_PATH}"
        )

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found: {CSV_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    participants = read_participants(CSV_PATH)

    print(f"Found {len(participants)} participants.")

    for index, participant in enumerate(participants, start=1):

        name = participant["username"]
        credential_id = participant["credential_id"].strip()

        if not credential_id:
            raise ValueError(f"Missing credential ID for {name}")

        output_png = OUTPUT_DIR / f"{credential_id}.png"

        add_name(
            TEMPLATE_PATH,
            name,
            output_png
        )

        print(f"[{index}] Generated certificate for: {name}")

    print("\nCertificate generation completed!")

    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
