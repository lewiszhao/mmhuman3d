from typing import Iterable, Optional, Tuple, Union

import torch
from pytorch3d.structures import Meshes

from mmhuman3d.core.cameras import MMCamerasBase
from .base_renderer import BaseRenderer
from .builder import RENDERER


@RENDERER.register_module(
    name=['Mesh', 'mesh', 'mesh_renderer', 'MeshRenderer'])
class MeshRenderer(BaseRenderer):
    """Render RGBA image with the help of camera system."""
    shader_type = 'SoftPhongShader'

    def __init__(
        self,
        resolution: Tuple[int, int] = None,
        device: Union[torch.device, str] = 'cpu',
        output_path: Optional[str] = None,
        out_img_format: str = '%06d.png',
        **kwargs,
    ) -> None:
        """Renderer for RGBA image of meshes.

        Args:
            resolution (Iterable[int]):
                (width, height) of the rendered images resolution.
            device (Union[torch.device, str], optional):
                You can pass a str or torch.device for cpu or gpu render.
                Defaults to 'cpu'.
            output_path (Optional[str], optional):
                Output path of the video or images to be saved.
                Defaults to None.
            out_img_format (str, optional): The image format string for
                saving the images.
                Defaults to '%06d.png'.
        """
        super().__init__(
            resolution=resolution,
            device=device,
            output_path=output_path,
            out_img_format=out_img_format,
            **kwargs)

    def forward(self,
                meshes: Optional[Meshes] = None,
                vertices: Optional[torch.Tensor] = None,
                faces: Optional[torch.Tensor] = None,
                cameras: Optional[MMCamerasBase] = None,
                images: Optional[torch.Tensor] = None,
                lights: Optional[torch.Tensor] = None,
                indexes: Optional[Iterable[int]] = None,
                **kwargs) -> Union[torch.Tensor, None]:
        """Render Meshes.

        Args:
            meshes (Optional[Meshes], optional): meshes to be rendered.
                Defaults to None.
            vertices (Optional[torch.Tensor], optional): vertices to be
                rendered. Should be passed together with faces.
                Defaults to None.
            faces (Optional[torch.Tensor], optional): faces of the meshes,
                should be passed together with the vertices.
                Defaults to None.
            images (Optional[torch.Tensor], optional): background images.
                Defaults to None.
            indexes (Optional[Iterable[int]], optional): indexes for images.
                Defaults to None.

        Returns:
            Union[torch.Tensor, None]: return tensor or None.
        """

        meshes = self._prepare_meshes(
            meshes, vertices, faces, device=self.device)
        self._update_resolution(cameras, **kwargs)
        fragments = self.rasterizer(meshes_world=meshes, cameras=cameras)

        rendered_images = self.shader(
            fragments=fragments,
            meshes=meshes,
            cameras=cameras,
            lights=self.lights if lights is None else lights)

        if self.output_path is not None:
            rgba = self.tensor2rgba(rendered_images)
            self._write_images(rgba, images, indexes)
        return rendered_images
