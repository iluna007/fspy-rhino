# fSpy Camera Utils for Rhino/Grasshopper
# Parses fSpy "Camera parameters as JSON" export and converts to Rhino camera data.
# See https://fspy.io/ - "Importing to other applications"

import json
import math
import System
import Rhino
from Rhino.Geometry import Point3d, Vector3d

# fSpy JSON keys (from CameraParameters export)
KEY_CAMERA_TRANSFORM = "cameraTransform"
KEY_ROWS = "rows"
KEY_PRINCIPAL_POINT = "principalPoint"
KEY_H_FOV = "horizontalFieldOfView"
KEY_V_FOV = "verticalFieldOfView"
KEY_IMAGE_W = "imageWidth"
KEY_IMAGE_H = "imageHeight"


def parse_fspy_json(json_input):
    """
    Parse fSpy camera parameters from either a file path or a JSON string.
    
    Args:
        json_input: str - path to .json file, or JSON string of camera parameters
    
    Returns:
        dict with keys: camera_location (Point3d), camera_direction (Vector3d),
        camera_up (Vector3d), camera_target (Point3d), horizontal_fov_rad, vertical_fov_rad,
        image_width, image_height, principal_point (dict x,y), target_distance, error (str or None)
    """
    result = {
        "camera_location": None,
        "camera_direction": None,
        "camera_up": None,
        "camera_target": None,
        "horizontal_fov_rad": None,
        "vertical_fov_rad": None,
        "image_width": None,
        "image_height": None,
        "principal_point": None,
        "target_distance": 100.0,
        "error": None
    }
    
    try:
        if json_input is None or str(json_input).strip() == "":
            result["error"] = "No JSON path or string provided"
            return result
        
        s = str(json_input).strip()
        # File path: no curly brace at start (no encoding= for IronPython compatibility)
        if not s.startswith("{"):
            try:
                with open(s, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except TypeError:
                with open(s, "r") as f:
                    data = json.load(f)
        else:
            data = json.loads(s)
        
        rows = data.get(KEY_CAMERA_TRANSFORM, {}).get(KEY_ROWS)
        if not rows or len(rows) < 4:
            result["error"] = "Invalid cameraTransform in JSON"
            return result
        
        # fSpy cameraTransform is world-from-camera (camera pose). Row-major 4x4.
        # Position = translation (column 3)
        tx = float(rows[0][3])
        ty = float(rows[1][3])
        tz = float(rows[2][3])
        result["camera_location"] = Point3d(tx, ty, tz)
        
        # Camera looks along -Z in OpenGL convention. So direction = -Z axis of camera in world.
        # Third column is camera's +Z, so look direction = -third column
        zx = float(rows[0][2])
        zy = float(rows[1][2])
        zz = float(rows[2][2])
        look = Vector3d(-zx, -zy, -zz)
        if look.Length > 1e-10:
            look.Unitize()
        result["camera_direction"] = look
        
        # Up = Y axis of camera (second column)
        ux = float(rows[0][1])
        uy = float(rows[1][1])
        uz = float(rows[2][1])
        up = Vector3d(ux, uy, uz)
        if up.Length > 1e-10:
            up.Unitize()
        result["camera_up"] = up
        
        # Default target distance (user can scale in Rhino)
        target_dist = float(data.get("targetDistance", 100.0))
        try:
            target_dist = max(0.1, float(target_dist))
        except (TypeError, ValueError):
            target_dist = 100.0
        result["target_distance"] = target_dist
        
        result["camera_target"] = Point3d(
            tx + look.X * target_dist,
            ty + look.Y * target_dist,
            tz + look.Z * target_dist
        )
        
        result["horizontal_fov_rad"] = float(data.get(KEY_H_FOV, 0))
        result["vertical_fov_rad"] = float(data.get(KEY_V_FOV, 0))
        result["image_width"] = int(data.get(KEY_IMAGE_W, 0))
        result["image_height"] = int(data.get(KEY_IMAGE_H, 0))
        result["principal_point"] = data.get(KEY_PRINCIPAL_POINT, {"x": 0, "y": 0})
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def fov_rad_to_rhino_half_angle_degrees(fov_rad):
    """Convert full FOV in radians to Rhino half-angle in degrees."""
    if fov_rad is None or fov_rad <= 0:
        return 30.0  # default
    return math.degrees(fov_rad * 0.5)
