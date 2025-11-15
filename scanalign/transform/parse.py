import os
from typing import Optional

from svgelements import SVG

from scanalign.transform.transform import transform_file, transform_path


def parse_svg(filename: str, debug_dir: Optional[str] = None):
    basename, extension = os.path.splitext(os.path.basename(filename))

    file = SVG.parse(filename)
    cut_data = transform_file(file)
    if cut_data is not None:
        print(cut_data.registration_marks)
        for layer_id, layer_paths in cut_data.layers.items():
            output = SVG(width=file.values["width"], height=file.values["height"], viewbox=file.viewbox)
            for path in layer_paths:
                for segment in transform_path(path):
                    output.append(segment)

            if debug_dir is not None:
                os.makedirs(debug_dir, exist_ok=True)
                output.write_xml(os.path.join(debug_dir, f"{basename}_{layer_id}{extension}"))
