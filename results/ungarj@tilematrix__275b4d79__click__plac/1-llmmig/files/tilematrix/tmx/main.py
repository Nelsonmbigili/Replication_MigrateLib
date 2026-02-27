import plac
import geojson
from shapely.geometry import box

import tilematrix
from tilematrix import TilePyramid


def tmx(
    pixelbuffer: ("Tile bounding box buffer in pixels. (default: 0)", int) = 0,
    tile_size: ("Tile size in pixels. (default: 256)", int) = 256,
    metatiling: ("TilePyramid metatile size. (default: 1)", int) = 1,
    grid: ("TilePyramid base grid. (default: geodetic)", str) = "geodetic",
    output_format: ("Print Tile ID or Tile bounding box as WKT or GeoJSON. (default: Tile)", str) = "Tile",
    version: ("Show version and exit", bool) = False,
):
    """
    TileMatrix CLI tool.
    """
    if version:
        print(tilematrix.__version__)
        return

    # Shared context
    ctx = {
        "pixelbuffer": pixelbuffer,
        "tile_size": tile_size,
        "metatiling": metatiling,
        "grid": grid,
        "output_format": output_format,
    }

    # Call the appropriate subcommand
    plac.Interpreter.call(globals(), ctx=ctx)


def bounds(ctx, tile: ("Tile ID (z, x, y)", int)):
    """Print Tile bounds."""
    z, x, y = tile
    print(
        "%s %s %s %s"
        % TilePyramid(
            ctx["grid"],
            tile_size=ctx["tile_size"],
            metatiling=ctx["metatiling"],
        )
        .tile(z, x, y)
        .bounds(pixelbuffer=ctx["pixelbuffer"])
    )


def bbox(ctx, tile: ("Tile ID (z, x, y)", int)):
    """Print Tile bounding box as geometry."""
    z, x, y = tile
    geom = (
        TilePyramid(
            ctx["grid"],
            tile_size=ctx["tile_size"],
            metatiling=ctx["metatiling"],
        )
        .tile(z, x, y)
        .bbox(pixelbuffer=ctx["pixelbuffer"])
    )
    if ctx["output_format"] in ["WKT", "Tile"]:
        print(geom)
    elif ctx["output_format"] == "GeoJSON":
        print(geojson.dumps(geom))


def tile(ctx, zoom: ("Zoom level", int), point: ("Point coordinates (x, y)", float)):
    """Print Tile containing POINT."""
    x, y = point
    tile = TilePyramid(
        ctx["grid"],
        tile_size=ctx["tile_size"],
        metatiling=ctx["metatiling"],
    ).tile_from_xy(x, y, zoom=zoom)
    if ctx["output_format"] == "Tile":
        print("%s %s %s" % tile.id)
    elif ctx["output_format"] == "WKT":
        print(tile.bbox(pixelbuffer=ctx["pixelbuffer"]))
    elif ctx["output_format"] == "GeoJSON":
        print(
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


def tiles(ctx, zoom: ("Zoom level", int), bounds: ("Bounding box (minx, miny, maxx, maxy)", float)):
    """Print Tiles from bounds."""
    tiles = TilePyramid(
        ctx["grid"],
        tile_size=ctx["tile_size"],
        metatiling=ctx["metatiling"],
    ).tiles_from_bounds(bounds, zoom=zoom)
    if ctx["output_format"] == "Tile":
        for tile in tiles:
            print("%s %s %s" % tile.id)
    elif ctx["output_format"] == "WKT":
        for tile in tiles:
            print(tile.bbox(pixelbuffer=ctx["pixelbuffer"]))
    elif ctx["output_format"] == "GeoJSON":
        print("{\n" '  "type": "FeatureCollection",\n' '  "features": [')
        try:
            tile = next(tiles)
            while True:
                gj = "    %s" % geojson.Feature(
                    geometry=tile.bbox(pixelbuffer=ctx["pixelbuffer"]),
                    properties=dict(zoom=tile.zoom, row=tile.row, col=tile.col),
                )
                try:
                    tile = next(tiles)
                    print(gj + ",")
                except StopIteration:
                    print(gj)
                    raise
        except StopIteration:
            pass
        print("  ]\n}")


def snap_bounds(ctx, zoom: ("Zoom level", int), bounds: ("Bounding box (minx, miny, maxx, maxy)", float)):
    """Snap bounds to tile grid."""
    print(
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


def snap_bbox(ctx, zoom: ("Zoom level", int), bounds: ("Bounding box (minx, miny, maxx, maxy)", float)):
    """Snap bbox to tile grid."""
    print(
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
    plac.call(tmx)
