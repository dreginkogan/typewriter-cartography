from enum import Enum
from pathlib import Path
from typing import Annotated, Tuple, Optional

import typer
import Map

app = typer.Typer(help="Turn geographic TIFFs into typewriter art maps.")

class AliasEnum(str, Enum):
    """Enum that also accepts aliases and is case-insensitive."""
    @classmethod
    def _aliases(cls) -> dict[str, str]:
        return {}

    @classmethod
    def _missing_(cls, value):
        key = str(value).lower()
        key = cls._aliases().get(key, key)
        for member in cls:
            if member.value == key:
                return member
        return None

    @classmethod
    def parse(cls, value: str) -> str:
        # returns the plain string, Typer then builds the enum
        return cls(value).value

    @classmethod
    def metavar(cls) -> str:
        return "|".join(list(m.value for m in cls) + list(cls._aliases()))


class CropOrientation(AliasEnum):
    """Orientation of the *paper-shaped crop* taken from the TIFF."""
    portrait = "portrait"
    landscape = "landscape"

    @classmethod
    def _aliases(cls):
        return {"p": "portrait", "l": "landscape"}


class DisplayOrientation(AliasEnum):
    """The orientation of the paper when displaying the map upright.
    Differs from CropOrientation: crop picks which part of the TIFF you keep, and orientation just has to do with the 'shape' of the 'cookie-cutter',
    display orients the typewriter map image such that it is consistent with how you want it displayed"""  # TODO: confirm against Map.py
    portrait = "portrait"
    landscape = "landscape"

    @classmethod
    def _aliases(cls):
        return {"p": "portrait", "l": "landscape"}


class PaperSize(AliasEnum):
    letter = "letter"
    a4 = "a4"

    @classmethod
    def _aliases(cls):
        return {"us": "letter", "usletter": "letter", "iso": "a4"}

class Mode(AliasEnum):
    '''
    Determines how the typewriter map is rendered, still a work in progress.'''
    bw = "bw"
    rgb = "rgb"

@app.command()
def make_tw_map(
    filepath: Annotated[Path, typer.Argument(exists=True, help="Input geographic TIFF path")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output PNG path.")] = Path("typewriter_map.png"),
    center: Annotated[
        Optional[Tuple[int, int]],
        typer.Option(help="Crop center as ROW COL in pixels (numpy order). Defaults to the TIFF's center."),
    ] = None,
    primary_dim: Annotated[int, typer.Option(help="Crop size in pixels along the primary dimension.")] = 2000,
    crop_orientation: Annotated[
        CropOrientation,
        typer.Option(parser=CropOrientation.parse, metavar=CropOrientation.metavar(), help="Orientation of the crop."),
    ] = CropOrientation.landscape,
    display_orientation: Annotated[
        DisplayOrientation,
        typer.Option(parser=DisplayOrientation.parse, metavar=DisplayOrientation.metavar(), help="Orientation of the paper when displaying the map."),
    ] = DisplayOrientation.landscape,
    paper_size: Annotated[
        PaperSize,
        typer.Option(parser=PaperSize.parse, metavar=PaperSize.metavar(), help="Paper size."),
    ] = PaperSize.letter,
    type_width: Annotated[float, typer.Option(help="Width in inches to type. Leave room for margins.")] = 6.5,
    levels: Annotated[int, typer.Option(help="Number of values elevations are binned into.")] = 4,
    water_threshold: Annotated[float, typer.Option(help="The elevation float under which a height gets registered as water.")] = 0.8,
    horizontal_keys_per_inch: Annotated[int, typer.Option(help="The number of keys per inch horizontally, on the physical typewriter")] = 10,
    vertical_keys_per_inch: Annotated[int, typer.Option(help="The number of keys per inch vertically, on the physical typewriter")] = 6,
    # TODO: implement different display modes, e.g. colors, characters, characters+colors 
    # mode: Annotated[
    #     Mode,
    #     typer.Option(parser=Mode.parse, metavar=Mode.metavar(), help="Output color mode."),
    # ] = Mode.rgb,
):
    """Crop, convert, and save a typewriter map."""
    m = Map.Map(str(filepath))

    if center is None:
        width, height = m.dims
        center = (height // 2, width // 2)

    m.crop_to_paper_aspect(center, crop_orientation.value, primary_dim, paper_size.value)
    m.to_typewriter_array(display_orientation.value, type_width, levels, water_threshold, horizontal_keys_per_inch=horizontal_keys_per_inch, vertical_keys_per_inch=vertical_keys_per_inch)
    m.to_typewriter_map("rgb", horizontal_keys_per_inch=horizontal_keys_per_inch, vertical_keys_per_inch=vertical_keys_per_inch).save(output)

if __name__ == "__main__":
    app()