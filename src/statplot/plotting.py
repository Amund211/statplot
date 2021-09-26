"""
Legend handler for adding images to the legend

Adapted from:
https://stackoverflow.com/questions/26029592/insert-image-in-matplotlib-legend
"""

from pathlib import Path

import numpy as np
from matplotlib.artist import Artist
from matplotlib.colors import to_rgba
from matplotlib.image import BboxImage
from matplotlib.legend_handler import HandlerBase
from matplotlib.pyplot import imread
from matplotlib.transforms import Bbox, TransformedBbox

from statplot.players import download_head_texture, get_head_path


class ImageHandler(HandlerBase):
    def __init__(self, image_path: Path, pad_width: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_data = imread(str(image_path))
        self.pad_width = pad_width

    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
        length = 2 * min(width, height)
        # length = max(width, height)

        missing_width = length - width
        missing_height = length - height
        if missing_width > 0:
            width += missing_width
            xdescent -= missing_width / 2

        if missing_height > 0:
            height += missing_height
            ydescent -= missing_height / 2
        bb = Bbox.from_bounds(xdescent, ydescent, width, height)

        tbb = TransformedBbox(bb, trans)
        image = BboxImage(tbb, interpolation="nearest")
        border_color = to_rgba(orig_handle.get_color())

        if self.pad_width > 0:
            # Embed image in larger image to add a border showing the artist color
            bordered_image = np.full(
                (
                    self.image_data.shape[0] + 2 * self.pad_width,
                    self.image_data.shape[1] + 2 * self.pad_width,
                    self.image_data.shape[2],
                ),
                border_color,
                dtype=np.float32,
            )

            bordered_image[
                self.pad_width : -self.pad_width,
                self.pad_width : -self.pad_width,
            ] = self.image_data
        else:
            bordered_image = self.image_data

        np.array(border_color)

        image.set_data(bordered_image)

        return [image]


def add_heads_to_legend(
    axis,
    items: list[tuple[Artist, str]],
    head_dir: Path,
    image_handler_kwargs: dict = {},
    **kwargs,
):
    """Given a list of tuples (artist, uuid) add the users head to the legend"""
    # Ensure we have all the heads we need
    for _, uuid in items:
        head_path = get_head_path(head_dir, uuid)
        if not head_path.is_file():
            download_head_texture(uuid, head_dir)

    axis.legend(
        handler_map={
            artist: ImageHandler(get_head_path(head_dir, uuid), **image_handler_kwargs)
            for artist, uuid in items
        },
        **kwargs,
    )
