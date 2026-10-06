"""Shared geometry for the backdrop: the page camera and the equirectangular HDRI.

The page (murmuration.html, paintSky) draws murmuration-sky.jpg, 3840x1600, with focal length
f = 800 / tan 23° = 1884.7 px (46° vertical field) and the horizon on row 0.8 * 1600 = 1280,
so the camera looks up by atan(480 / f) = 14.29°. Directions here are x right, y up, z forward,
as in the page.
"""
import math

import cv2
import numpy as np

JW, JH = 3840, 1600
F = (JH / 2) / math.tan(math.radians(23))
HORIZON_ROW = 0.8 * JH


def read_hdr(path):
    """Linear RGB float32 (H, W, 3) from a Radiance .hdr."""
    im = cv2.imread(str(path), cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(path)
    return im[:, :, ::-1].astype(np.float32)


def read_rgb8(path):
    im = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(path)
    return im[:, :, ::-1]


def camera_rays(w, h, yaw, pitch, roll=0.0):
    """Unit world directions for every pixel of a w x h view with the page camera's focal length
    (scaled to w) looking up by `pitch` and turned by `yaw` (degrees)."""
    f = F * w / JW
    x = (np.arange(w) + .5 - w / 2) / f
    y = -(np.arange(h) + .5 - h / 2) / f
    X, Y = np.meshgrid(x, y)
    d = np.stack([X, Y, np.ones_like(X)], -1)
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    r, p, q = map(math.radians, (roll, pitch, yaw))
    Rz = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(p), math.sin(p)], [0, -math.sin(p), math.cos(p)]])
    Ry = np.array([[math.cos(q), 0, math.sin(q)], [0, 1, 0], [-math.sin(q), 0, math.cos(q)]])
    return d @ (Ry @ Rx @ Rz).T


def dir_to_equirect(d, W, H):
    """Pixel coordinates in a W x H equirect map (Blender/Poly Haven layout: longitude increases to
    the left across the image, the centre column is longitude 0)."""
    lon = np.arctan2(d[..., 0], d[..., 2])
    lat = np.arcsin(np.clip(d[..., 1], -1, 1))
    u = (0.5 - lon / (2 * np.pi)) * W
    v = (0.5 - lat / np.pi) * H
    return np.mod(u, W), v


def equirect_to_dir(u, v, W, H):
    lon = (0.5 - u / W) * 2 * np.pi
    lat = (0.5 - v / H) * np.pi
    return np.stack([np.cos(lat) * np.sin(lon), np.sin(lat), np.cos(lat) * np.cos(lon)], -1)


def reproject(eq, w, h, yaw, pitch, roll=0.0):
    """Sample an equirect image into a w x h page-camera view (bilinear)."""
    d = camera_rays(w, h, yaw, pitch, roll)
    u, v = dir_to_equirect(d, eq.shape[1], eq.shape[0])
    return cv2.remap(eq, (u - .5).astype(np.float32), (v - .5).astype(np.float32),
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)


def luminance(rgb):
    return rgb @ np.array([.2126, .7152, .0722], np.float32)
