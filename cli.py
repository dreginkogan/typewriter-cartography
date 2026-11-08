from enum import Enum
from pathlib import Path
from typing import Annotated, Tuple

import typer
import Map

app = typer.Typer(help="Turn geographic TIFFs into typewriter art maps.")

class CropOrientation(str, Enum):
    # TODO make aliases s.t. "p" = "portrait", "l" = "landscape"
    portrait = "portrait"
    landscape = "landscape"

class DisplayOrientation(str, Enum):
    # TODO documentation on what each of these values actually means, and how it diferrs from the other orientation
    portrait = "portrait"
    landscape = "landscape"

class PaperSize(str, Enum):
    # TODO aliases
    letter = "letter"
    a4 = "a4"

class Mode(str, Enum):
    #TODO see Map.py comments
    bw = "bw"
    rgb = "rgb"

@app.command()
def make_tw_map(
    #TODO annotate each option well and make this less cluttered
    filepath: Annotated[Path, typer.Argument(exists=True, help="Input image")],
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("typewriter_map.png"),
    center: Annotated[Tuple[int, int], typer.Option(help="Crop center as X Y in pixels")] = (0, 0),
    primary_dim: Annotated[int, typer.Option(help="Crop size in pixels along the primary dimension")] = 2000,
    crop_orientation: CropOrientation = CropOrientation.landscape,
    display_orientation: DisplayOrientation = DisplayOrientation.landscape,
    paper_size: PaperSize = PaperSize.letter,
    type_width: Annotated[float, typer.Option(help="Width in inches to type, make sure to leave margins")] = 6.5,
    levels: int = 4,
    water_threshold: float = 0.2,
    mode: Mode = Mode.rgb,
):
    """Crop, convert, and save a typewriter map."""
    m = Map.Map(str(filepath))
    m.crop_to_paper_aspect(center, crop_orientation, primary_dim, paper_size)
    m.to_typewriter_array(display_orientation, type_width, levels, water_threshold)
    m.to_typewriter_map(mode.value).save(output)
    typer.echo(f"Saved {output}")


if __name__ == "__main__":
    app()