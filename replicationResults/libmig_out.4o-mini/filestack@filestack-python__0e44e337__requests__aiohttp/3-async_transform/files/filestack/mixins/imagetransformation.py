import filestack.models
from filestack import utils
import aiohttp
import asyncio


class ImageTransformationMixin:
    """
    All transformations and related/dependent tasks live here. They can
    be directly called by Transformation or Filelink objects.
    """
    async def resize(self, width=None, height=None, fit=None, align=None):
        return await self._add_transform_task('resize', locals())

    async def crop(self, dim=None):
        return await self._add_transform_task('crop', locals())

    async def rotate(self, deg=None, exif=None, background=None):
        return await self._add_transform_task('rotate', locals())

    async def flip(self):
        return await self._add_transform_task('flip', locals())

    async def flop(self):
        return await self._add_transform_task('flop', locals())

    async def watermark(self, file=None, size=None, position=None):
        return await self._add_transform_task('watermark', locals())

    async def detect_faces(self, minsize=None, maxsize=None, color=None, export=None):
        return await self._add_transform_task('detect_faces', locals())

    async def crop_faces(self, mode=None, width=None, height=None, faces=None, buffer=None):
        return await self._add_transform_task('crop_faces', locals())

    async def pixelate_faces(self, faces=None, minsize=None, maxsize=None, buffer=None, amount=None, blur=None, type=None):
        return await self._add_transform_task('pixelate_faces', locals())

    async def round_corners(self, radius=None, blur=None, background=None):
        return await self._add_transform_task('round_corners', locals())

    async def vignette(self, amount=None, blurmode=None, background=None):
        return await self._add_transform_task('vignette', locals())

    async def polaroid(self, color=None, rotate=None, background=None):
        return await self._add_transform_task('polaroid', locals())

    async def torn_edges(self, spread=None, background=None):
        return await self._add_transform_task('torn_edges', locals())

    async def shadow(self, blur=None, opacity=None, vector=None, color=None, background=None):
        return await self._add_transform_task('shadow', locals())

    async def circle(self, background=None):
        return await self._add_transform_task('circle', locals())

    async def border(self, width=None, color=None, background=None):
        return await self._add_transform_task('border', locals())

    async def sharpen(self, amount=None):
        return await self._add_transform_task('sharpen', locals())

    async def blur(self, amount=None):
        return await self._add_transform_task('blur', locals())

    async def monochrome(self):
        return await self._add_transform_task('monochrome', locals())

    async def blackwhite(self, threshold=None):
        return await self._add_transform_task('blackwhite', locals())

    async def sepia(self, tone=None):
        return await self._add_transform_task('sepia', locals())

    async def pixelate(self, amount=None):
        return await self._add_transform_task('pixelate', locals())

    async def oil_paint(self, amount=None):
        return await self._add_transform_task('oil_paint', locals())

    async def negative(self):
        return await self._add_transform_task('negative', locals())

    async def modulate(self, brightness=None, hue=None, saturation=None):
        return await self._add_transform_task('modulate', locals())

    async def partial_pixelate(self, amount=None, blur=None, type=None, objects=None):
        return await self._add_transform_task('partial_pixelate', locals())

    async def partial_blur(self, amount=None, blur=None, type=None, objects=None):
        return await self._add_transform_task('partial_blur', locals())

    async def collage(self, files=None, margin=None, width=None, height=None, color=None, fit=None, autorotate=None):
        return await self._add_transform_task('collage', locals())

    async def upscale(self, upscale=None, noise=None, style=None):
        return await self._add_transform_task('upscale', locals())

    async def enhance(self, preset=None):
        return await self._add_transform_task('enhance', locals())

    async def redeye(self):
        return await self._add_transform_task('redeye', locals())

    async def ascii(self, background=None, foreground=None, colored=None, size=None, reverse=None):
        return await self._add_transform_task('ascii', locals())

    async def filetype_conversion(self, format=None, background=None, page=None, density=None, compress=None,
                            quality=None, strip=None, colorspace=None, secure=None,
                            docinfo=None, pageformat=None, pageorientation=None):
        return await self._add_transform_task('output', locals())

    async def no_metadata(self):
        return await self._add_transform_task('no_metadata', locals())

    def quality(self, value=None):
        return self._add_transform_task('quality', locals())

    async def zip(self):
        return await self._add_transform_task('zip', locals())

    async def fallback(self, file=None, cache=None):
        return await self._add_transform_task('fallback', locals())

    async def pdf_info(self, colorinfo=None):
        return await self._add_transform_task('pdfinfo', locals())

    async def pdf_convert(self, pageorientation=None, pageformat=None, pages=None, metadata=None):
        return await self._add_transform_task('pdfconvert', locals())

    async def minify_js(self, gzip=None, use_babel_polyfill=None, keep_fn_name=None, keep_class_name=None,
                  mangle=None, merge_vars=None, remove_console=None, remove_undefined=None, targets=None):
        return await self._add_transform_task('minify_js', locals())

    async def minify_css(self, level=None, gzip=None):
        return await self._add_transform_task('minify_css', locals())

    async def av_convert(self, *, preset=None, force=None, title=None, extname=None, filename=None,
                   width=None, height=None, upscale=None, aspect_mode=None, two_pass=None,
                   video_bitrate=None, fps=None, keyframe_interval=None, location=None,
                   watermark_url=None, watermark_top=None, watermark_bottom=None,
                   watermark_right=None, watermark_left=None, watermark_width=None, watermark_height=None,
                   path=None, access=None, container=None, audio_bitrate=None, audio_sample_rate=None,
                   audio_channels=None, clip_length=None, clip_offset=None):

        new_transform = await self._add_transform_task('video_convert', locals())
        
        async with aiohttp.ClientSession() as session:
            async with session.get(new_transform.url) as response:
                response_data = await response.json()
                uuid = response_data['uuid']
                timestamp = response_data['timestamp']

        return filestack.models.AudioVisual(
            new_transform.url, uuid, timestamp, apikey=new_transform.apikey, security=new_transform.security
        )

    async def auto_image(self):
        return await self._add_transform_task('auto_image', locals())

    async def doc_to_images(self, pages=None, engine=None, format=None, quality=None, density=None, hidden_slides=None):
        return await self._add_transform_task('doc_to_images', locals())

    async def smart_crop(self, mode=None, width=None, height=None, fill_color=None, coords=None):
        return await self._add_transform_task('smart_crop', locals())

    async def pdfcreate(self, engine=None):
        return await self._add_transform_task('pdfcreate', locals())

    async def animate(self, delay=None, loop=None, width=None, height=None, fit=None, align=None, background=None):
        return await self._add_transform_task('animate', locals())

    async def _add_transform_task(self, transformation, params):
        if isinstance(self, filestack.models.Transformation):
            instance = self
        else:
            instance = filestack.models.Transformation(apikey=None, security=self.security, handle=self.handle)

        params.pop('self')
        params = {k: v for k, v in params.items() if v is not None}

        transformation_url = await utils.return_transform_task(transformation, params)
        instance._transformation_tasks.append(transformation_url)

        return instance
