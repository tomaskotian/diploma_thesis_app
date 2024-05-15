"""
File: CamValues.py
Author: Tomas Kotian
Date: 15.5.2024
Description: Values for camera focus and magnification
"""

class Cam_values:
    """
    magnification_deg - define angle for specify magnification \n
    focus_distance - define distances for specific magnification to camera be focused
    """
    magnification_deg = {
        0.7: 0,
        0.8: 13,
        0.9: 27,
        1: 40,
        1.1: 48,
        1.2: 56,
        1.3: 64,
        1.4: 72,
        1.5: 80,
        1.6: 84,
        1.7: 88,
        1.8: 92,
        1.9: 96,
        2: 100,
        2.1: 106,
        2.2: 112,
        2.3: 118,
        2.4: 124,
        2.5: 130,
        2.6: 134,
        2.7: 138,
        2.8: 152,
        2.9: 156,
        3: 150,
        3.1: 156,
        3.2: 162,
        3.3: 168,
        3.4: 174,
        3.5: 180,
        3.6: 184,
        3.7: 188,
        3.8: 192,
        3.9: 196,
        4: 200,
        4.1: 206,
        4.2: 212,
        4.3: 218,
        4.4: 224,
        4.5: 230,
        4.6: 234,
        4.7: 238,
        4.8: 242,
        4.9: 246,
        5: 250,
        5.1: 255,
        5.2: 260,
        5.3: 265,
        5.4: 270,
        5.5: 275,
        5.6: 280,
    }
    focus_distance = {
        0.7: 0,
        1: 40,
        1.5: 80,
        2: 100,
        2.5: 130,
        3: 150,
        3.5: 180,
        4: 200,
        4.5: 230,
        5: 250,
        5.6: 280,
    }