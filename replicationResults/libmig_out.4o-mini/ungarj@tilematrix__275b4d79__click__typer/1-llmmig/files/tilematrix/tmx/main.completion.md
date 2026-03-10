### Explanation of Changes

To migrate the code from the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: Changed the import from `click` to `typer`.
2. **Version Option**: The `@click.version_option` decorator was replaced with `typer.Option` in the main command function.
3. **Group and Command Decorators**: The `@click.group()` and `@click.command()` decorators were replaced with `@typer.Typer()` for the main group and `@typer.command()` for subcommands.
4. **Options and Arguments**: The `@click.option()` and `@click.argument()` decorators were replaced with `typer.Option()` and `typer.Argument()`, respectively. The type hints were adjusted to use `int` and `float` directly instead of `click.INT` and `click.FLOAT`.
5. **Context Handling**: The context object handling was simplified since `typer` automatically manages the context and parameters passed to commands.
6. **Echoing Output**: The `click.echo()` function was replaced with `typer.echo()` for printing output.

The overall structure and logic of the code remain unchanged, adhering to the original coding style.

### Modified Code

```python
import typer
import geojson
from shapely.geometry import box

import tilematrix
from tilematrix import TilePyramid

app = typer.Typer()

@app.callback()
def version_callback():
    """Show the version of the application."""
    typer.echo(f"Version: {tilematrix.__version__}")

@app.command()
def tmx(
    pixelbuffer: int = typer.Option(0, "--pixelbuffer", "-p", help="Tile bounding box buffer in pixels. (default: 0)"),
    tile_size: int = typer.Option(256, "--tile_size", "-s", help="Tile size in pixels. (default: 256)"),
    metatiling: int = typer.Option(1, "--metatiling", "-m", help="TilePyramid metatile size. (default: 1)"),
    grid: str = typer.Option("geodetic", "--grid", "-g", help="TilePyramid base grid. (default: geodetic)"),
    output_format: str = typer.Option("Tile", "--output_format", "-f", help="Print Tile ID or Tile bounding box as WKT or GeoJSON. (default: Tile)"),
):
    """Main command for tile operations."""
    ctx = {
        "pixelbuffer": pixelbuffer,
        "tile_size": tile_size,
        "metatiling": metatiling,
        "grid": grid,
        "output_format": output_format,
    }

@app.command(short_help="Tile bounds.")
def bounds(tile: list[int] = typer.Argument(..., min=3, max=3)):
    """Print Tile bounds."""
    typer.echo(
        "%s %s %s %s"
        % TilePyramid(
            ctx["grid"],
            tile_size=ctx["tile_size"],
            metatiling=ctx["metatiling"],
        )
        .tile(*tile)
        .bounds(pixelbuffer=ctx["pixelbuffer"])
    )

@app.command(short_help="Tile bounding box.")
def bbox(tile: list[int] = typer.Argument(..., min=3, max=3)):
    """Print Tile bounding box as geometry."""
    geom = (
        TilePyramid(
            ctx["grid"],
            tile_size=ctx["tile_size"],
            metatiling=ctx["metatiling"],
        )
        .tile(*tile)
        .bbox(pixelbuffer=ctx["pixelbuffer"])
    )
    if ctx["output_format"] in ["WKT", "Tile"]:
        typer.echo(geom)
    elif ctx["output_format"] == "GeoJSON":
        typer.echo(geojson.dumps(geom))

@app.command(short_help="Tile from point.")
def tile(zoom: int = typer.Argument(...), point: list[float] = typer.Argument(..., min=2, max=2)):
    """Print Tile containing POINT.."""
    tile = TilePyramid(
        ctx["grid"],
        tile_size=ctx["tile_size"],
        metatiling=ctx["metatiling"],
    ).tile_from_xy(*point, zoom=zoom)
    if ctx["output_format"] == "Tile":
        typer.echo("%s %s %s" % tile.id)
    elif ctx["output_format"] == "WKT":
        typer.echo(tile.bbox(pixelbuffer=ctx["pixelbuffer"]))
    elif ctx["output_format"] == "GeoJSON":
        typer.echo(
            geojson.dumps(
                geojson.FeatureCollection(
                    [
                        geojson.Feature(
                            geometry=tile.bbox(pixelbuffer=ctx["pixelbuffer"]),
                            properties=dict(zoom=tile.zoom, row=tile.row, col=tile.col),
                        )
                    ]
                )
            )
        )

@app.command(short_help="Tiles from bounds.")
def tiles(zoom: int = typer.Argument(...), bounds: list[float] = typer.Argument(..., min=4, max=4)):
    """Print Tiles from bounds."""
    tiles = TilePyramid(
        ctx["grid"],
        tile_size=ctx["tile_size"],
        metatiling=ctx["metatiling"],
    ).tiles_from_bounds(bounds, zoom=zoom)
    if ctx["output_format"] == "Tile":
        for tile in tiles:
            typer.echo("%s %s %s" % tile.id)
    elif ctx["output_format"] == "WKT":
        for tile in tiles:
            typer.echo(tile.bbox(pixelbuffer=ctx["pixelbuffer"]))
    elif ctx["output_format"] == "GeoJSON":
        typer.echo("{\n" '  "type": "FeatureCollection",\n' '  "features": [')
        # print tiles as they come and only add comma if there is a next tile
        try:
            tile = next(tiles)
            while True:
                gj = "    %s" % geojson.Feature(
                    geometry=tile.bbox(pixelbuffer=ctx["pixelbuffer"]),
                    properties=dict(zoom=tile.zoom, row=tile.row, col=tile.col),
                )
                try:
                    tile = next(tiles)
                    typer.echo(gj + ",")
                except StopIteration:
                    typer.echo(gj)
                    raise
        except StopIteration:
            pass
        typer.echo("  ]\n" "}")

@app.command(short_help="Snap bounds to tile grid.")
def snap_bounds(zoom: int = typer.Argument(...), bounds: list[float] = typer.Argument(..., min=4, max=4)):
    """Snap bounds to tile grid."""
    typer.echo(
        "%s %s %s %s"
        % tilematrix.snap_bounds(
            bounds=bounds,
            tile_pyramid=TilePyramid(
                ctx["grid"],
                tile_size=ctx["tile_size"],
                metatiling=ctx["metatiling"],
            ),
            zoom=zoom,
            pixelbuffer=ctx["pixelbuffer"],
        )
    )

@app.command(short_help="Snap bbox to tile grid.")
def snap_bbox(zoom: int = typer.Argument(...), bounds: list[float] = typer.Argument(..., min=4, max=4)):
    """Snap bbox to tile grid."""
    typer.echo(
        box(
            *tilematrix.snap_bounds(
                bounds=bounds,
                tile_pyramid=TilePyramid(
                    ctx["grid"],
                    tile_size=ctx["tile_size"],
                    metatiling=ctx["metatiling"],
                ),
                zoom=zoom,
                pixelbuffer=ctx["pixelbuffer"],
            )
        )
    )

if __name__ == "__main__":
    app()
```