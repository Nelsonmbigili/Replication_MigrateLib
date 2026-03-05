import plac
import geojson
from shapely.geometry import box

import tilematrix
from tilematrix import TilePyramid


def tmx(pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic", output_format="Tile"):
@click.version_option(version=tilematrix.__version__, message="%(version)s")
@click.group()
@click.option(
    "--pixelbuffer",
    "-p",
    nargs=1,
    type=click.INT,
    default=0,
    help="Tile bounding box buffer in pixels. (default: 0)",
)
@click.option(
    "--tile_size",
    "-s",
    nargs=1,
    type=click.INT,
    default=256,
    help="Tile size in pixels. (default: 256)",
)
@click.option(
    "--metatiling",
    "-m",
    nargs=1,
    type=click.INT,
    default=1,
    help="TilePyramid metatile size. (default: 1)",
)
@click.option(
    "--grid",
    "-g",
    type=click.Choice(["geodetic", "mercator"]),
    default="geodetic",
    help="TilePyramid base grid. (default: geodetic)",
)
@click.option(
    "--output_format",
    "-f",
    type=click.Choice(["Tile", "WKT", "GeoJSON"]),
    default="Tile",
    help="Print Tile ID or Tile bounding box as WKT or GeoJSON. (default: Tile)",
)
@click.pass_context
def tmx(ctx, **kwargs):
    ctx.obj = dict(**kwargs)
    """Tile management commands."""
    plac.call(bounds, pixelbuffer=pixelbuffer, tile_size=tile_size, metatiling=metatiling, grid=grid, output_format=output_format)


@plac.annotations(
    pixelbuffer=("Tile bounding box buffer in pixels. (default: 0)", "option", "p", int),
    tile_size=("Tile size in pixels. (default: 256)", "option", "s", int),
    metatiling=("TilePyramid metatile size. (default: 1)", "option", "m", int),
    grid=("TilePyramid base grid. (default: geodetic)", "option", "g"),
    output_format=("Print Tile ID or Tile bounding box as WKT or GeoJSON. (default: Tile)", "option", "f"),
)
def bounds(tile, pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic", output_format="Tile"):
    """Print Tile bounds."""
    click.echo(
        "%s %s %s %s"
        % TilePyramid(
            grid,
            tile_size=tile_size,
            metatiling=metatiling,
        )
        .tile(*tile)
        .bounds(pixelbuffer=pixelbuffer)
    )


@plac.annotations(
    tile=("TILE", "argument", "TILE", int),
)
def bbox(tile, pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic", output_format="Tile"):
    """Print Tile bounding box as geometry."""
    geom = (
        TilePyramid(
            grid,
            tile_size=tile_size,
            metatiling=metatiling,
        )
        .tile(*tile)
        .bbox(pixelbuffer=pixelbuffer)
    )
    if output_format in ["WKT", "Tile"]:
        click.echo(geom)
    elif output_format == "GeoJSON":
        click.echo(geojson.dumps(geom))


@plac.annotations(
    zoom=("ZOOM", "argument", "ZOOM", int),
    point=("POINT", "argument", "POINT", float),
)
def tile(point, zoom, pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic", output_format="Tile"):
    """Print Tile containing POINT.."""
    tile = TilePyramid(
        grid,
        tile_size=tile_size,
        metatiling=metatiling,
    ).tile_from_xy(*point, zoom=zoom)
    if output_format == "Tile":
        click.echo("%s %s %s" % tile.id)
    elif output_format == "WKT":
        click.echo(tile.bbox(pixelbuffer=pixelbuffer))
    elif output_format == "GeoJSON":
        click.echo(
            geojson.dumps(
                geojson.FeatureCollection(
                    [
                        geojson.Feature(
                            geometry=tile.bbox(pixelbuffer=pixelbuffer),
                            properties=dict(zoom=tile.zoom, row=tile.row, col=tile.col),
                        )
                    ]
                )
            )
        )


@plac.annotations(
    zoom=("ZOOM", "argument", "ZOOM", int),
    bounds=("BOUNDS", "argument", "BOUNDS", float),
)
def tiles(bounds, zoom, pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic", output_format="Tile"):
    """Print Tiles from bounds."""
    tiles = TilePyramid(
        grid,
        tile_size=tile_size,
        metatiling=metatiling,
    ).tiles_from_bounds(bounds, zoom=zoom)
    if output_format == "Tile":
        for tile in tiles:
            click.echo("%s %s %s" % tile.id)
    elif output_format == "WKT":
        for tile in tiles:
            click.echo(tile.bbox(pixelbuffer=pixelbuffer))
    elif output_format == "GeoJSON":
        click.echo("{\n" '  "type": "FeatureCollection",\n' '  "features": [')
        # print tiles as they come and only add comma if there is a next tile
        try:
            tile = next(tiles)
            while True:
                gj = "    %s" % geojson.Feature(
                    geometry=tile.bbox(pixelbuffer=pixelbuffer),
                    properties=dict(zoom=tile.zoom, row=tile.row, col=tile.col),
                )
                try:
                    tile = next(tiles)
                    click.echo(gj + ",")
                except StopIteration:
                    click.echo(gj)
                    raise
        except StopIteration:
            pass
        click.echo("  ]\n" "}")


@plac.annotations(
    zoom=("ZOOM", "argument", "ZOOM", int),
    bounds=("BOUNDS", "argument", "BOUNDS", float),
)
def snap_bounds(bounds, zoom, pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic"):
    """Snap bounds to tile grid."""
    click.echo(
        "%s %s %s %s"
        % tilematrix.snap_bounds(
            bounds=bounds,
            tile_pyramid=TilePyramid(
                grid,
                tile_size=tile_size,
                metatiling=metatiling,
            ),
            zoom=zoom,
            pixelbuffer=pixelbuffer,
        )
    )


@plac.annotations(
    zoom=("ZOOM", "argument", "ZOOM", int),
    bounds=("BOUNDS", "argument", "BOUNDS", float),
)
def snap_bbox(bounds, zoom, pixelbuffer=0, tile_size=256, metatiling=1, grid="geodetic"):
    """Snap bbox to tile grid."""
    click.echo(
        box(
            *tilematrix.snap_bounds(
                bounds=bounds,
                tile_pyramid=TilePyramid(
                    grid,
                    tile_size=tile_size,
                    metatiling=metatiling,
                ),
                zoom=zoom,
                pixelbuffer=pixelbuffer,
            )
        )
    )

if __name__ == "__main__":
    plac.call(tmx)