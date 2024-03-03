import io

import streamlit as st
from PIL import Image, ImageOps


def mirror_and_pad_image(image):
    # Create a vertically mirrored image
    mirrored_image = ImageOps.flip(image)

    # Create a new image with the same width and twice the height plus 20 pixels for padding
    new_image = Image.new("RGB", (image.width, image.height * 2 + 20), color="white")

    # Paste the original image at the top of the new image
    new_image.paste(image, (0, image.height + 20))

    # Paste the mirrored image at the bottom of the new image, leaving a 20-pixel gap
    new_image.paste(mirrored_image, (0, 0))

    return new_image


def resize_images(images):
    # Determine the smallest image size
    min_size = min(min(image.width, image.height) for image in images)

    resized_images = []
    for image in images:
        # Calculate the aspect ratio
        aspect_ratio = image.width / image.height

        # Calculate the new size while maintaining the aspect ratio
        if image.width > image.height:
            new_size = (int(min_size * aspect_ratio), min_size)
        else:
            new_size = (min_size, int(min_size / aspect_ratio))

        # Resize the image and append it to the list
        resized_image = image.resize(new_size, Image.LANCZOS)
        # Create a new white image of the same size

        resized_images.append(resized_image)

    return resized_images


def create_horizontal_sync(images):
    # Calculate the total width and find the max height
    total_width = sum(image.width for image in images)
    max_height = max(image.height for image in images)

    # Create a new image with the correct size
    new_image = Image.new("RGB", (total_width, max_height), color="white")

    x_offset = 20
    for image in images:
        # Paste the current image into the composite image
        new_image.paste(image, (x_offset, 0))
        x_offset += image.width

    return new_image


# Set up the title of your app
st.title("D&D Character Initiative List Creator")

# Create a file uploader to allow users to upload multiple images
uploaded_files = st.file_uploader(
    "Choose character images", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
)

images = []
for uploaded_file in uploaded_files:
    # Read the uploaded images
    image_bytes = io.BytesIO(uploaded_file.read())
    image = Image.open(image_bytes)
    # Check if the image has an alpha (transparency) channel
    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        # Create a new white background image
        background = Image.new("RGBA", image.size, (255, 255, 255))
        # Paste the uploaded image onto the background
        background.paste(
            image, mask=image.split()[3] if image.mode == "RGBA" else None
        )  # 3 is the alpha channel
        image = background.convert("RGB")
    images.append(image)

if images:  # Check if any images were uploaded
    resized_images = resize_images(images)
    transformed_images = [mirror_and_pad_image(image) for image in resized_images]
    composite_image = create_horizontal_sync(transformed_images)

    # Convert the PIL image to bytes to display it in Streamlit
    # Calculate the new width while maintaining the aspect ratio
    new_height = int(10 * 300 / 2.54)  # 10 cm in pixels at 300 DPI
    aspect_ratio = composite_image.width / composite_image.height
    new_width = int(new_height * aspect_ratio)

    # Resize the composite image
    resized_composite_image = composite_image.resize(
        (new_width, new_height), Image.LANCZOS
    )

    # Convert the PIL image to bytes to display it in Streamlit
    img_bytes = io.BytesIO()
    resized_composite_image.save(img_bytes, format="JPEG")
    st.image(img_bytes.getvalue(), caption="Composite Image")
