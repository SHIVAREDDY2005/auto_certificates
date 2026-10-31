
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ==============================
# PROJECT PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "data" / "hackathon_certificate.png"
CSV_PATH = BASE_DIR / "data" / "names.csv"

FONT_PATH = BASE_DIR / "fonts" / "Montserrat-VariableFont_wght.ttf"

QR_DIR = BASE_DIR / "qr_codes"

OUTPUT_DIR = BASE_DIR / "email_certificates"


# ==============================
# CERTIFICATE NAME SETTINGS
# ==============================

NAME_CENTER_X = 1280
NAME_CENTER_Y = 2150

MAX_NAME_WIDTH = 11000

NAME_COLOR = "#393078"

START_FONT_SIZE = 100
MIN_FONT_SIZE = 100


# ==============================
# QR CODE SETTINGS
# ==============================

# ==============================
# QR CODE SETTINGS
# ==============================

QR_SIZE = 500

QR_LEFT = 55
QR_TOP = 1550

# ID SETTINGS
ID_FONT_SIZE = 38
ID_COLOR = "#393078"
CREDENTIAL_COLOR = "black"

# ==============================
# FONT LOADER
# ==============================

def load_font(size):

    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Font not found: {FONT_PATH}"
        )

    font = ImageFont.truetype(
        str(FONT_PATH),
        size
    )

    # Montserrat Bold
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

        required_columns = {
            "username",
            "credential_id",
            "random_id"
        }

        if (
            not reader.fieldnames
            or not required_columns.issubset(reader.fieldnames)
        ):
            raise ValueError(
                "CSV must contain username, credential_id and random_id columns."
            )

        participants = []

        for row in reader:

            username = (row.get("username") or "").strip()
            credential_id = (row.get("credential_id") or "").strip()
            random_id = (row.get("random_id") or "").strip()

            if not username:
                continue

            if not credential_id:
                raise ValueError(
                    f"Missing credential_id for participant: {username}"
                )

            if not random_id:
                raise ValueError(
                    f"Missing random_id for participant: {username}"
                )

            participants.append({
                "username": username,
                "credential_id": credential_id,
                "random_id": random_id
            })

    if not participants:
        raise ValueError("No valid participants found in CSV.")

    # Prevent accidental overwriting from duplicate IDs
    credential_ids = [p["credential_id"] for p in participants]

    if len(credential_ids) != len(set(credential_ids)):
        raise ValueError("Duplicate credential IDs found in CSV.")

    return participants


# ==============================
# ADD NAME, QR CODE AND RANDOM ID
# ==============================

def add_name(
    template_path,
    name,
    credential_id,
    random_id,
    output_png
):

    image = Image.open(template_path).convert("RGBA")

    draw = ImageDraw.Draw(image)

    # --------------------------
    # ADD PARTICIPANT NAME
    # --------------------------

    font_size = START_FONT_SIZE
    font = load_font(font_size)

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

    if text_width > MAX_NAME_WIDTH:
        raise ValueError(
            f"Participant name is too long: {name}"
        )

    draw.text(
        (NAME_CENTER_X, NAME_CENTER_Y),
        name,
        fill=NAME_COLOR,
        font=font,
        anchor="mm"
    )

    # --------------------------
    # LOAD PARTICIPANT QR CODE
    # --------------------------

    qr_path = QR_DIR / f"{credential_id}.png"

    if not qr_path.exists():
        raise FileNotFoundError(
            f"QR code not found: {qr_path}"
        )

    qr_image = Image.open(qr_path).convert("RGB")

    # Resize QR code
    qr_image = qr_image.resize(
        (QR_SIZE, QR_SIZE),
        Image.Resampling.NEAREST
    )

    # --------------------------
    # ADD WHITE QR BACKGROUND
    # --------------------------

    qr_background = Image.new(
        "RGBA",
        (QR_SIZE, QR_SIZE),
        "white"
    )

    qr_background.alpha_composite(
        qr_image.convert("RGBA")
    )

    # --------------------------
    # PLACE QR ON CERTIFICATE
    # --------------------------

    if (
        QR_LEFT < 0
        or QR_TOP < 0
        or QR_LEFT + QR_SIZE > image.width
        or QR_TOP + QR_SIZE > image.height
    ):
        raise ValueError(
            "QR position exceeds certificate dimensions."
        )

    image.alpha_composite(
        qr_background,
        (QR_LEFT, QR_TOP)
    )

    # --------------------------
    # ADD RANDOM ID ABOVE QR
    # --------------------------

    id_font = load_font(ID_FONT_SIZE)

    id_center_x = QR_LEFT + QR_SIZE // 2
    id_y = QR_TOP - 12

    draw.text(
        (id_center_x, id_y),
        random_id,
        fill=ID_COLOR,
        font=id_font,
        anchor="mm"
    )

    # --------------------------
    # SAVE PNG
    # --------------------------

    output_png.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(
        output_png,
        "PNG"
    )

    # --------------------------
    # SAVE PDF
    # --------------------------

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

    # Check required files
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE_PATH}"
        )

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found: {CSV_PATH}"
        )

    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Font not found: {FONT_PATH}"
        )

    if not QR_DIR.exists():
        raise FileNotFoundError(
            f"QR directory not found: {QR_DIR}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    participants = read_participants(CSV_PATH)

    print(f"\nFound {len(participants)} participants.\n")

    # Generate certificates
    for index, participant in enumerate(participants, start=1):

        name = participant["username"]
        credential_id = participant["credential_id"]
        random_id = f"Credential ID : {participant["random_id"]}" 

        output_png = OUTPUT_DIR / f"{credential_id}.png"

        add_name(
            TEMPLATE_PATH,
            name,
            credential_id,
            random_id,
            output_png
        )

        print(
            f"[{index}/{len(participants)}] "
            f"Generated: {credential_id} | {name} | {random_id}"
        )

    print("\n================================")
    print("CERTIFICATE GENERATION COMPLETE")
    print("================================")

    print(f"Total certificates: {len(participants)}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
