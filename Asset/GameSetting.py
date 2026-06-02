ENTITY_TYPE = {
    "bullet": 0,
    "enemy": 1,
    "player": 2,
    "obstacle": 3,
}

GRID_CONFIG = {
    "cell_w": 40,
    "cell_h": 40,
    "number_of_cells_w": 50,
    "number_of_cells_h": 50,
}

COLOR_CONFIG = {
    "cooldown": (100, 180, 255),
    "reload": (255, 140, 40),
    "scatter_angel": (255, 255, 0),
    "capacity": (100, 255, 100),
    "phy_damage": (255, 255, 255),
    "exp_damage": (255, 100, 0),
    "bur_damage": (255, 200, 0),
    "speed": (100, 255, 150),
    "normal_bullet": (200, 200, 150, 255),
    "enemy": (255, 0, 0, 255),
}

# Bullet Type: "Type Name", {stats}, {draw_info}
# stats: speed, damage, {attribute_modifier}, info
# draw_info: list of draw_shape (draw_shape: type of shape, {shape_info})
BULLET_CONFIG = {
    0: [
        "Normal Bullet",
        {
            "speed": 10,
            "physical_damage": 5,
            "radius": 3,
            "info": "The most basic bullet, deal physical damage",
            "draw_info": {
                "circle": [{"radius": 3, "color": COLOR_CONFIG["normal_bullet"]}]
            },
        },
        {
            "circle": [
                {
                    "pos_x": 0.5,
                    "pos_y": 0.5,
                    "size": 0.4,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ]
        },
    ],
    1: [
        "Light Bullet",
        {
            "speed": 6,
            "physical_damage": 3,
            "radius": 2,
            "capacity_modifier": 20,
            "cooldown_modifier": -0.1,
            "scatter_angel_modifier": 5,
            "info": "Deal physical damage with high capacity, low speed, low damage and narrow scatter angle",
            "draw_info": {
                "circle": [{"radius": 2, "color": COLOR_CONFIG["normal_bullet"]}]
            },
        },
        {
            "circle": [
                {
                    "pos_x": 0.5,
                    "pos_y": 0.5,
                    "size": 0.3,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ]
        },
    ],
    2: [
        "Heavy Bullet",
        {
            "speed": 16,
            "physical_damage": 15,
            "radius": 4,
            "capacity_modifier": -15,
            "cooldown_modifier": 0.1,
            "scatter_angel_modifier": -5,
            "info": "Deal physical damage with low capacity, high speed, high damage and wide scatter angle",
            "draw_info": {
                "circle": [{"radius": 4, "color": COLOR_CONFIG["normal_bullet"]}]
            },
        },
        {
            "circle": [
                {
                    "pos_x": 0.5,
                    "pos_y": 0.5,
                    "size": 0.5,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ]
        },
    ],
    3: [
        "Grenades",
        {
            "speed": 4,
            "explosion_damage": 10,
            "radius": 5,
            "explosion_radius": 80,
            "capacity_modifier": -20,
            "cooldown_modifier": 0.5,
            "info": "Deal explosion damage to enemies in an area. The explosion occurs either when its lifetime ends or when it collides with an enemy or an obstacle.",
            "draw_info": {
                "circle": [
                    {"radius": 5, "color": (50, 50, 50, 255)},
                    {"radius": 4, "color": (100, 100, 100, 255)},
                ]
            },
        },
        {
            "circle": [
                {"pos_x": 0.5, "pos_y": 0.5, "size": 0.6, "color": (50, 50, 50, 255)},
                {
                    "pos_x": 0.5,
                    "pos_y": 0.5,
                    "size": 0.5,
                    "color": (100, 100, 100, 255),
                },
            ],
            "line": [
                {
                    "start_x": 0.65,
                    "start_y": 0.3,
                    "end_x": 0.77,
                    "end_y": 0.18,
                    "width": 0.05,
                    "color": (100, 100, 100, 255),
                }
            ],
        },
    ],
    4: [
        "Laser",
        {
            "speed": 10,
            "burn_damage": 2,
            "radius": 2,
            "scatter_angel_modifier": -10,
            "info": "Deals burn damage to enemies in a straight line.",
            "draw_info": {"line": [{"width": 2, "color": (150, 255, 120, 255)}]},
        },
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.15,
                    "end_x": 0.5,
                    "end_y": 0.85,
                    "width": 0.3,
                    "color": (150, 255, 120, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.15,
                    "end_x": 0.5,
                    "end_y": 0.85,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
            ]
        },
    ],
}

ATTRIBUTE_MODIFIER_CONFIG = {
    0: [
        "Add Cooldown I",
        {"cooldown_modifier": 0.1, "info": "Add cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    1: [
        "Add Cooldown II",
        {"cooldown_modifier": 0.2, "info": "Add cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    2: [
        "Add Cooldown III",
        {"cooldown_modifier": 0.3, "info": "Add cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    3: [
        "Add Cooldown IV",
        {"cooldown_modifier": 0.4, "info": "Add cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    4: [
        "Add Cooldown V",
        {"cooldown_modifier": 0.5, "info": "Add cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    5: [
        "Sub Cooldown I",
        {"cooldown_modifier": -0.1, "info": "Subtract cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    6: [
        "Sub Cooldown II",
        {"cooldown_modifier": -0.2, "info": "Subtract cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    7: [
        "Sub Cooldown III",
        {"cooldown_modifier": -0.3, "info": "Subtract cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    8: [
        "Sub Cooldown IV",
        {"cooldown_modifier": -0.4, "info": "Subtract cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    9: [
        "Sub Cooldown V",
        {"cooldown_modifier": -0.5, "info": "Subtract cooldown"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    10: [
        "Add Reload I",
        {"reload_modifier": 0.2, "info": "Add reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    11: [
        "Add Reload II",
        {"reload_modifier": 0.5, "info": "Add reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    12: [
        "Add Reload III",
        {"reload_modifier": 1.0, "info": "Add reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    13: [
        "Add Reload IV",
        {"reload_modifier": 1.5, "info": "Add reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    14: [
        "Add Reload V",
        {"reload_modifier": 2.5, "info": "Add reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    15: [
        "Sub Reload I",
        {"reload_modifier": -0.2, "info": "Subtract reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    16: [
        "Sub Reload II",
        {"reload_modifier": -0.5, "info": "Subtract reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    17: [
        "Sub Reload III",
        {"reload_modifier": -1.0, "info": "Subtract reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    18: [
        "Sub Reload IV",
        {"reload_modifier": -1.5, "info": "Subtract reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    19: [
        "Sub Reload V",
        {"reload_modifier": -2.5, "info": "Subtract reload"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["reload"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["reload"],
                },
            ],
        },
    ],
    20: [
        "Add Scatter Angel I",
        {"scatter_angel_modifier": 5, "info": "Add scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    21: [
        "Add Scatter Angel II",
        {"scatter_angel_modifier": 10, "info": "Add scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    22: [
        "Add Scatter Angel III",
        {"scatter_angel_modifier": 15, "info": "Add scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    23: [
        "Add Scatter Angel IV",
        {"scatter_angel_modifier": 20, "info": "Add scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    24: [
        "Add Scatter Angel V",
        {"scatter_angel_modifier": 30, "info": "Add scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    25: [
        "Sub Scatter Angel I",
        {"scatter_angel_modifier": -5, "info": "Subtract scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    26: [
        "Sub Scatter Angel II",
        {"scatter_angel_modifier": -10, "info": "Subtract scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    27: [
        "Sub Scatter Angel III",
        {"scatter_angel_modifier": -15, "info": "Subtract scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    28: [
        "Sub Scatter Angel IV",
        {"scatter_angel_modifier": -20, "info": "Subtract scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    29: [
        "Sub Scatter Angel V",
        {"scatter_angel_modifier": -30, "info": "Subtract scatter angel"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["scatter_angel"],
                },
            ],
        },
    ],
    30: [
        "Add Capacity I",
        {"capacity_modifier": 5, "info": "Add capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    31: [
        "Add Capacity II",
        {"capacity_modifier": 10, "info": "Add capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.1,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    32: [
        "Add Capacity III",
        {"capacity_modifier": 15, "info": "Add capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.15,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    33: [
        "Add Capacity IV",
        {"capacity_modifier": 20, "info": "Add capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.2,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    34: [
        "Add Capacity V",
        {"capacity_modifier": 30, "info": "Add capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.25,
                    "width": 0.25,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    35: [
        "Sub Capacity I",
        {"capacity_modifier": -5, "info": "Subtract capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    36: [
        "Sub Capacity II",
        {"capacity_modifier": -10, "info": "Subtract capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.1,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    37: [
        "Sub Capacity III",
        {"capacity_modifier": -15, "info": "Subtract capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.15,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    38: [
        "Sub Capacity IV",
        {"capacity_modifier": -20, "info": "Subtract capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.2,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    39: [
        "Sub Capacity V",
        {"capacity_modifier": -30, "info": "Subtract capacity"},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.25,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["capacity"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.75,
                    "width": 0.25,
                    "color": COLOR_CONFIG["capacity"],
                },
            ],
        },
    ],
    50: [
        "Add Speed I",
        {"bullet_speed_modifier": 3, "info": "Add bullet speed"},
        {
            "line": [
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.70,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": COLOR_CONFIG["speed"],
                },
            ],
        },
    ],
    51: [
        "Add Speed II",
        {"bullet_speed_modifier": 6, "info": "Add bullet speed"},
        {
            "line": [
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.1,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.70,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.1,
                    "color": COLOR_CONFIG["speed"],
                },
            ],
        },
    ],
    52: [
        "Add Speed III",
        {"bullet_speed_modifier": 10, "info": "Add bullet speed"},
        {
            "line": [
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.15,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.70,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.15,
                    "color": COLOR_CONFIG["speed"],
                },
            ],
        },
    ],
    53: [
        "Add Speed IV",
        {"bullet_speed_modifier": 15, "info": "Add bullet speed"},
        {
            "line": [
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.2,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.70,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.2,
                    "color": COLOR_CONFIG["speed"],
                },
            ],
        },
    ],
    54: [
        "Add Speed V",
        {"bullet_speed_modifier": 25, "info": "Add bullet speed"},
        {
            "line": [
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.25,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.70,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.25,
                    "color": COLOR_CONFIG["speed"],
                },
            ],
        },
    ],
    55: [
        "Add Physical Damage I",
        {"physical_damage_modifier": 3, "info": "Add physical damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.40,
                    "end_x": 0.40,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.60,
                    "end_x": 0.40,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    56: [
        "Add Physical Damage II",
        {"physical_damage_modifier": 6, "info": "Add physical damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.40,
                    "end_x": 0.40,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.60,
                    "end_x": 0.40,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.1,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.1,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.1,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    57: [
        "Add Physical Damage III",
        {"physical_damage_modifier": 10, "info": "Add physical damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.40,
                    "end_x": 0.40,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.60,
                    "end_x": 0.40,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.15,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.15,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.15,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    58: [
        "Add Physical Damage IV",
        {"physical_damage_modifier": 18, "info": "Add physical damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.40,
                    "end_x": 0.40,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.60,
                    "end_x": 0.40,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    59: [
        "Add Physical Damage IV",
        {"physical_damage_modifier": 30, "info": "Add physical damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.40,
                    "end_x": 0.40,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.60,
                    "end_x": 0.40,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.25,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.25,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.25,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    60: [
        "Add Explosion Damage I",
        {"explosion_damage_modifier": 2, "info": "Add explosion damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["exp_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.30,
                    "start_y": 0.40,
                    "end_x": 0.30,
                    "end_y": 0.30,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.30,
                    "start_y": 0.60,
                    "end_x": 0.30,
                    "end_y": 0.70,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.10,
                    "start_y": 0.50,
                    "end_x": 0.20,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    61: [
        "Add Explosion Damage II",
        {"explosion_damage_modifier": 4, "info": "Add explosion damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["exp_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.30,
                    "start_y": 0.40,
                    "end_x": 0.30,
                    "end_y": 0.30,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.30,
                    "start_y": 0.60,
                    "end_x": 0.30,
                    "end_y": 0.70,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.10,
                    "start_y": 0.50,
                    "end_x": 0.20,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.1,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.1,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.1,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    62: [
        "Add Explosion Damage III",
        {"explosion_damage_modifier": 7, "info": "Add explosion damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["exp_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.30,
                    "start_y": 0.40,
                    "end_x": 0.30,
                    "end_y": 0.30,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.30,
                    "start_y": 0.60,
                    "end_x": 0.30,
                    "end_y": 0.70,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.10,
                    "start_y": 0.50,
                    "end_x": 0.20,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.15,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.15,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.15,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    63: [
        "Add Explosion Damage IV",
        {"explosion_damage_modifier": 12, "info": "Add explosion damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["exp_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.30,
                    "start_y": 0.40,
                    "end_x": 0.30,
                    "end_y": 0.30,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.30,
                    "start_y": 0.60,
                    "end_x": 0.30,
                    "end_y": 0.70,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.10,
                    "start_y": 0.50,
                    "end_x": 0.20,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.2,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    64: [
        "Add Explosion Damage V",
        {"explosion_damage_modifier": 20, "info": "Add explosion damage"},
        {
            "circle": [
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["exp_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.30,
                    "start_y": 0.40,
                    "end_x": 0.30,
                    "end_y": 0.30,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.30,
                    "start_y": 0.60,
                    "end_x": 0.30,
                    "end_y": 0.70,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.10,
                    "start_y": 0.50,
                    "end_x": 0.20,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.20,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.25,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.25,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.30,
                    "end_x": 0.70,
                    "end_y": 0.20,
                    "width": 0.25,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    100: [
        "Speed damage bonus",
        {
            "reload_modifier": 0.2,
            "info": "Bullet’s Physical damage is modified by adding half of the bullet’s speed value, and each bullet can only receive this bonus once.",
        },
        {
            "circle": [
                {
                    "pos_x": 0.25,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.15,
                    "start_y": 0.40,
                    "end_x": 0.35,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.15,
                    "start_y": 0.60,
                    "end_x": 0.35,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.30,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.1,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.70,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.1,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.20,
                    "end_x": 0.50,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.50,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.50,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    101: [
        "Damage Speed bonus",
        {
            "reload_modifier": 0.2,
            "info": "Bullet’s speed is modified by adding half of the bullet’s Physical damage value, and each bullet can only receive this bonus once.",
        },
        {
            "circle": [
                {
                    "pos_x": 0.75,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["phy_damage"],
                }
            ],
            "line": [
                {
                    "start_x": 0.85,
                    "start_y": 0.40,
                    "end_x": 0.65,
                    "end_y": 0.60,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.85,
                    "start_y": 0.60,
                    "end_x": 0.65,
                    "end_y": 0.40,
                    "width": 0.1,
                    "color": COLOR_CONFIG["phy_damage"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.30,
                    "end_x": 0.30,
                    "end_y": 0.50,
                    "width": 0.1,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.70,
                    "end_x": 0.30,
                    "end_y": 0.50,
                    "width": 0.1,
                    "color": COLOR_CONFIG["speed"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.20,
                    "end_x": 0.50,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.30,
                    "end_x": 0.50,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.30,
                    "end_x": 0.50,
                    "end_y": 0.20,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
}

PROJECTILE_MODIFIER_CONFIG = {
    0: [
        "F Split",
        {
            "info": "After the condition is triggered, the bullet will split into 2 bullets (-45~45 degrees), dealing half damage.",
            "default_trigger": "hit",
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.65,
                    "size": 0.3,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.75,
                    "end_x": 0.50,
                    "end_y": 0.95,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.65,
                    "end_x": 0.25,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.65,
                    "end_x": 0.75,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.25,
                    "end_x": 0.20,
                    "end_y": 0.40,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.25,
                    "end_x": 0.40,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.25,
                    "end_x": 0.80,
                    "end_y": 0.40,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.25,
                    "end_x": 0.60,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
            ],
        },
    ],
    1: [
        "B Split",
        {
            "info": "After the condition is triggered, the bullet will split into 2 bullets (135~225 degrees), dealing half damage.",
            "default_trigger": "hit",
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.35,
                    "size": 0.3,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.45,
                    "end_x": 0.50,
                    "end_y": 0.65,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.35,
                    "end_x": 0.25,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.35,
                    "end_x": 0.75,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.75,
                    "end_x": 0.20,
                    "end_y": 0.60,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.75,
                    "end_x": 0.40,
                    "end_y": 0.70,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.75,
                    "end_x": 0.80,
                    "end_y": 0.60,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.75,
                    "end_x": 0.60,
                    "end_y": 0.70,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
            ],
        },
    ],
    2: [
        "Penetrate",
        {
            "info": "The bullet can penetrate through enemies one additional time.",
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.5,
                    "size": 0.3,
                    "color": COLOR_CONFIG["enemy"],
                }
            ],
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.50,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.40,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.60,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
            ],
        },
    ],
    3: [
        "Bounce",
        {
            "info": "The bullet can bounce off enemies and walls one additional time.",
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.70,
                    "size": 0.2,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ],
            "line": [
                {
                    "start_x": 0.15,
                    "start_y": 0.75,
                    "end_x": 0.85,
                    "end_y": 0.75,
                    "width": 0.08,
                    "color": (150, 150, 150, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.70,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.70,
                    "end_x": 0.75,
                    "end_y": 0.35,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.35,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.35,
                    "end_x": 0.60,
                    "end_y": 0.40,
                    "width": 0.05,
                    "color": (200, 200, 200, 255),
                },
            ],
        },
    ],
    4: [
        "Explosive",
        {
            "info": "The bullet will explosion dealing damage to enemies in a 40 radius, dealing explosive damage equal to half of the final total(phy + exp + bur) damage.",
            "default_trigger": "hit",
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.30,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "pos_x": 0.30,
                    "pos_y": 0.70,
                    "size": 0.10,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "pos_x": 0.15,
                    "pos_y": 0.85,
                    "size": 0.10,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.35,
                    "end_x": 0.50,
                    "end_y": 0.20,
                    "width": 0.08,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.65,
                    "end_x": 0.50,
                    "end_y": 0.80,
                    "width": 0.08,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.35,
                    "start_y": 0.50,
                    "end_x": 0.20,
                    "end_y": 0.50,
                    "width": 0.08,
                    "color": COLOR_CONFIG["exp_damage"],
                },
                {
                    "start_x": 0.65,
                    "start_y": 0.50,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.08,
                    "color": COLOR_CONFIG["exp_damage"],
                },
            ],
        },
    ],
}

TRIGGER_MODIFIER_CONFIG = {
    0: [
        "Hit",
        {"info": "Switch trigger to hit.", "default_trigger": "hit"},
        {
            "circle": [
                {
                    "pos_x": 0.60,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ],
            "line": [
                {
                    "start_x": 0.65,
                    "start_y": 0.25,
                    "end_x": 0.65,
                    "end_y": 0.75,
                    "width": 0.08,
                    "color": (150, 150, 150, 255),
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.50,
                    "end_x": 0.60,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.50,
                    "end_x": 0.45,
                    "end_y": 0.35,
                    "width": 0.05,
                    "color": COLOR_CONFIG["bur_damage"],
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.50,
                    "end_x": 0.45,
                    "end_y": 0.65,
                    "width": 0.05,
                    "color": COLOR_CONFIG["bur_damage"],
                },
            ],
        },
    ],
    1: [
        "Lifetime",
        {"info": "Switch trigger to lifetime."},
        {
            "circle": [
                {
                    "pos_x": 0.25,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": COLOR_CONFIG["normal_bullet"],
                }
            ],
            "line": [
                {
                    "start_x": 0.25,
                    "start_y": 0.50,
                    "end_x": 0.40,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": (180, 180, 180, 255),
                },
                {
                    "start_x": 0.45,
                    "start_y": 0.50,
                    "end_x": 0.55,
                    "end_y": 0.50,
                    "width": 0.04,
                    "color": (130, 130, 130, 255),
                },
                {
                    "start_x": 0.60,
                    "start_y": 0.50,
                    "end_x": 0.66,
                    "end_y": 0.50,
                    "width": 0.03,
                    "color": (90, 90, 90, 255),
                },
                {
                    "start_x": 0.68,
                    "start_y": 0.38,
                    "end_x": 0.82,
                    "end_y": 0.62,
                    "width": 0.06,
                    "color": (220, 80, 80, 255),
                },
                {
                    "start_x": 0.68,
                    "start_y": 0.62,
                    "end_x": 0.82,
                    "end_y": 0.38,
                    "width": 0.06,
                    "color": (220, 80, 80, 255),
                },
            ],
        },
    ],
    2: [
        "Time 0.1s",
        {"info": "Switch trigger to 0.1s time elapsed."},
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.16,
                    "size": 0.12,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.60,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.50,
                    "color": (30, 30, 30, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.10,
                    "color": (200, 200, 200, 255),
                },
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.615,
                    "end_y": 0.385,
                    "width": 0.04,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.32,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    3: [
        "Time 0.2s",
        {"info": "Switch trigger to 0.2s time elapsed."},
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.16,
                    "size": 0.12,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.60,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.50,
                    "color": (30, 30, 30, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.10,
                    "color": (200, 200, 200, 255),
                },
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.64,
                    "end_y": 0.50,
                    "width": 0.04,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.32,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    4: [
        "Time 0.5s",
        {"info": "Switch trigger to 0.5s time elapsed."},
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.16,
                    "size": 0.12,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.60,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.50,
                    "color": (30, 30, 30, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.10,
                    "color": (200, 200, 200, 255),
                },
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.64,
                    "width": 0.04,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.32,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
    5: [
        "Time 1.0s",
        {"info": "Switch trigger to 1.0s time elapsed."},
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.16,
                    "size": 0.12,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.60,
                    "color": (200, 200, 200, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.50,
                    "color": (30, 30, 30, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.10,
                    "color": (200, 200, 200, 255),
                },
            ],
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.36,
                    "end_y": 0.50,
                    "width": 0.04,
                    "color": COLOR_CONFIG["cooldown"],
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.32,
                    "width": 0.05,
                    "color": COLOR_CONFIG["cooldown"],
                },
            ],
        },
    ],
}

MULTIBULLET_MODIFIER_CONFIG = {
    0: [
        "Package",
        {
            "info": "When trigger condition is met, target bullet will summon another bullet from the card slot behind it.",
            "default_trigger": "hit",
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.5,
                    "color": COLOR_CONFIG["normal_bullet"],
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.3,
                    "color": (100, 100, 100, 255),
                },
            ],
        },
    ],
    1: [
        "Double Bullet",
        {
            "info": "Simultaneously activate 2 bullets or multi-bullet card after this card"
        },
        {
            "circle": [
                {
                    "pos_x": 0.35,
                    "pos_y": 0.35,
                    "size": 0.22,
                    "color": (255, 200, 80, 255),
                },
                {
                    "pos_x": 0.65,
                    "pos_y": 0.35,
                    "size": 0.22,
                    "color": (255, 200, 80, 255),
                },
            ],
            "line": [
                # x
                {
                    "start_x": 0.30,
                    "start_y": 0.60,
                    "end_x": 0.42,
                    "end_y": 0.72,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.42,
                    "start_y": 0.60,
                    "end_x": 0.30,
                    "end_y": 0.72,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                # 2
                {
                    "start_x": 0.55,
                    "start_y": 0.58,
                    "end_x": 0.70,
                    "end_y": 0.58,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.58,
                    "end_x": 0.70,
                    "end_y": 0.66,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.66,
                    "end_x": 0.55,
                    "end_y": 0.74,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.55,
                    "start_y": 0.74,
                    "end_x": 0.70,
                    "end_y": 0.74,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    2: [
        "Triple Bullet",
        {
            "info": "Simultaneously activate 3 bullets or multi-bullet card after this card."
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.25,
                    "size": 0.22,
                    "color": (255, 200, 80, 255),
                },
                {
                    "pos_x": 0.30,
                    "pos_y": 0.50,
                    "size": 0.22,
                    "color": (255, 200, 80, 255),
                },
                {
                    "pos_x": 0.70,
                    "pos_y": 0.50,
                    "size": 0.22,
                    "color": (255, 200, 80, 255),
                },
            ],
            "line": [
                # x
                {
                    "start_x": 0.30,
                    "start_y": 0.68,
                    "end_x": 0.42,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.42,
                    "start_y": 0.68,
                    "end_x": 0.30,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                # 3
                {
                    "start_x": 0.55,
                    "start_y": 0.66,
                    "end_x": 0.70,
                    "end_y": 0.66,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.66,
                    "end_x": 0.70,
                    "end_y": 0.73,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.55,
                    "start_y": 0.73,
                    "end_x": 0.70,
                    "end_y": 0.73,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.73,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.55,
                    "start_y": 0.80,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
    3: [
        "Quadruple Bullet",
        {
            "info": "Simultaneously activate 4 bullets or multi-bullet card after this card."
        },
        {
            "circle": [
                {
                    "pos_x": 0.35,
                    "pos_y": 0.28,
                    "size": 0.20,
                    "color": (255, 200, 80, 255),
                },
                {
                    "pos_x": 0.65,
                    "pos_y": 0.28,
                    "size": 0.20,
                    "color": (255, 200, 80, 255),
                },
                {
                    "pos_x": 0.35,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": (255, 200, 80, 255),
                },
                {
                    "pos_x": 0.65,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": (255, 200, 80, 255),
                },
            ],
            "line": [
                # x
                {
                    "start_x": 0.30,
                    "start_y": 0.68,
                    "end_x": 0.42,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.42,
                    "start_y": 0.68,
                    "end_x": 0.30,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                # 4
                {
                    "start_x": 0.55,
                    "start_y": 0.66,
                    "end_x": 0.55,
                    "end_y": 0.73,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.55,
                    "start_y": 0.73,
                    "end_x": 0.70,
                    "end_y": 0.73,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.66,
                    "end_x": 0.70,
                    "end_y": 0.80,
                    "width": 0.05,
                    "color": (255, 255, 255, 255),
                },
            ],
        },
    ],
}

TRAJECTORY_MODIFIER_CONFIG = {
    0: [
        "Chaotic Trajectory",
        {
            "info": "The velocity of bullet will randomly change every 0.2 second.",
            "physical_damage": 5,
        },
        {
            "line": [
                {
                    "start_x": 0.25,
                    "start_y": 0.70,
                    "end_x": 0.40,
                    "end_y": 0.40,
                    "width": 0.05,
                    "color": (180, 100, 255, 255),
                },
                {
                    "start_x": 0.40,
                    "start_y": 0.40,
                    "end_x": 0.50,
                    "end_y": 0.60,
                    "width": 0.05,
                    "color": (180, 100, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.60,
                    "end_x": 0.65,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (180, 100, 255, 255),
                },
                {
                    "start_x": 0.65,
                    "start_y": 0.30,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": (180, 100, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.50,
                    "end_x": 0.70,
                    "end_y": 0.45,
                    "width": 0.05,
                    "color": (180, 100, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.50,
                    "end_x": 0.80,
                    "end_y": 0.40,
                    "width": 0.05,
                    "color": (180, 100, 255, 255),
                },
            ]
        },
    ],
    1: [
        "Horizontal Trajectory",
        {"info": "The velocity only available in x-axis.", "physical_damage": 5},
        {
            "line": [
                {
                    "start_x": 0.20,
                    "start_y": 0.50,
                    "end_x": 0.80,
                    "end_y": 0.50,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.50,
                    "end_x": 0.35,
                    "end_y": 0.35,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.20,
                    "start_y": 0.50,
                    "end_x": 0.35,
                    "end_y": 0.65,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.50,
                    "end_x": 0.65,
                    "end_y": 0.35,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.80,
                    "start_y": 0.50,
                    "end_x": 0.65,
                    "end_y": 0.65,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
            ]
        },
    ],
    2: [
        "Vertical Trajectory",
        {"info": "The velocity only available in y-axis.", "physical_damage": 5},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.20,
                    "end_x": 0.50,
                    "end_y": 0.80,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.20,
                    "end_x": 0.35,
                    "end_y": 0.35,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.20,
                    "end_x": 0.65,
                    "end_y": 0.35,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.80,
                    "end_x": 0.35,
                    "end_y": 0.65,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.80,
                    "end_x": 0.65,
                    "end_y": 0.65,
                    "width": 0.06,
                    "color": (100, 200, 255, 255),
                },
            ]
        },
    ],
    3: [
        "S Shape Trajectory",
        {"info": "The bullet will move in S shape.", "physical_damage": 5},
        {
            "line": [
                {
                    "start_x": 0.65,
                    "start_y": 0.25,
                    "end_x": 0.35,
                    "end_y": 0.25,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.35,
                    "start_y": 0.25,
                    "end_x": 0.35,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.35,
                    "start_y": 0.50,
                    "end_x": 0.65,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.65,
                    "start_y": 0.50,
                    "end_x": 0.65,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.65,
                    "start_y": 0.75,
                    "end_x": 0.35,
                    "end_y": 0.75,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.25,
                    "end_x": 0.58,
                    "end_y": 0.15,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.70,
                    "start_y": 0.25,
                    "end_x": 0.58,
                    "end_y": 0.35,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
            ]
        },
    ],
    4: [
        "O Shape Trajectory",
        {"info": "The bullet will move in O shape.", "physical_damage": 5},
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.60,
                    "color": (100, 255, 180, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.50,
                    "color": (30, 30, 30, 255),
                },
            ],
            "line": [
                {
                    "start_x": 0.75,
                    "start_y": 0.50,
                    "end_x": 0.90,
                    "end_y": 0.60,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.50,
                    "end_x": 0.60,
                    "end_y": 0.55,
                    "width": 0.05,
                    "color": (100, 255, 180, 255),
                },
            ],
        },
    ],
    5: [
        "T Shape Trajectory",
        {
            "info": "The bullet will turn left or right after moving 0.3 second",
            "physical_damage": 5,
        },
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.80,
                    "end_x": 0.50,
                    "end_y": 0.50,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.25,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.75,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.30,
                    "end_x": 0.38,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.30,
                    "end_x": 0.28,
                    "end_y": 0.43,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.30,
                    "end_x": 0.62,
                    "end_y": 0.30,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.30,
                    "end_x": 0.72,
                    "end_y": 0.43,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
            ]
        },
    ],
    6: [
        "V Shape Trajectory",
        {
            "info": "The bullet will turn back after moving 0.3 second",
            "physical_damage": 5,
        },
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.85,
                    "end_x": 0.50,
                    "end_y": 0.40,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.40,
                    "end_x": 0.25,
                    "end_y": 0.65,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.40,
                    "end_x": 0.75,
                    "end_y": 0.65,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.65,
                    "end_x": 0.38,
                    "end_y": 0.65,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.25,
                    "start_y": 0.65,
                    "end_x": 0.25,
                    "end_y": 0.52,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.65,
                    "end_x": 0.75,
                    "end_y": 0.52,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
                {
                    "start_x": 0.75,
                    "start_y": 0.65,
                    "end_x": 0.62,
                    "end_y": 0.65,
                    "width": 0.05,
                    "color": (255, 120, 120, 255),
                },
            ]
        },
    ],
    7: [
        "Circle",
        {
            "info": "The bullet will surround the player in a circle.",
            "physical_damage": 5,
        },
        {
            "circle": [
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.20,
                    "color": (0, 150, 255, 255),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.65,
                    "color": (255, 220, 100, 150),
                },
                {
                    "pos_x": 0.50,
                    "pos_y": 0.50,
                    "size": 0.61,
                    "color": (30, 30, 30, 255),
                },
                {
                    "pos_x": 0.80,
                    "pos_y": 0.50,
                    "size": 0.15,
                    "color": (255, 200, 80, 255),
                },
            ]
        },
    ],
    8: [
        "Accelerate",
        {
            "info": "The bullet will accelerate in a same direction it shoots.",
            "physical_damage": 5,
        },
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.75,
                    "end_x": 0.50,
                    "end_y": 0.65,
                    "width": 0.04,
                    "color": (150, 255, 100, 120),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.65,
                    "end_x": 0.45,
                    "end_y": 0.70,
                    "width": 0.04,
                    "color": (150, 255, 100, 120),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.65,
                    "end_x": 0.55,
                    "end_y": 0.70,
                    "width": 0.04,
                    "color": (150, 255, 100, 120),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.55,
                    "end_x": 0.50,
                    "end_y": 0.40,
                    "width": 0.06,
                    "color": (150, 255, 100, 180),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.40,
                    "end_x": 0.43,
                    "end_y": 0.47,
                    "width": 0.06,
                    "color": (150, 255, 100, 180),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.40,
                    "end_x": 0.57,
                    "end_y": 0.47,
                    "width": 0.06,
                    "color": (150, 255, 100, 180),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.30,
                    "end_x": 0.50,
                    "end_y": 0.10,
                    "width": 0.08,
                    "color": (150, 255, 100, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.10,
                    "end_x": 0.40,
                    "end_y": 0.20,
                    "width": 0.08,
                    "color": (150, 255, 100, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.10,
                    "end_x": 0.60,
                    "end_y": 0.20,
                    "width": 0.08,
                    "color": (150, 255, 100, 255),
                },
            ]
        },
    ],
    9: [
        "Decelerate",
        {"info": "The bullet will decelerate until stop.", "physical_damage": 5},
        {
            "line": [
                {
                    "start_x": 0.50,
                    "start_y": 0.85,
                    "end_x": 0.50,
                    "end_y": 0.60,
                    "width": 0.08,
                    "color": (255, 150, 100, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.60,
                    "end_x": 0.40,
                    "end_y": 0.70,
                    "width": 0.08,
                    "color": (255, 150, 100, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.60,
                    "end_x": 0.60,
                    "end_y": 0.70,
                    "width": 0.08,
                    "color": (255, 150, 100, 255),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.50,
                    "end_x": 0.50,
                    "end_y": 0.35,
                    "width": 0.05,
                    "color": (255, 150, 100, 180),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.35,
                    "end_x": 0.44,
                    "end_y": 0.41,
                    "width": 0.05,
                    "color": (255, 150, 100, 180),
                },
                {
                    "start_x": 0.50,
                    "start_y": 0.35,
                    "end_x": 0.56,
                    "end_y": 0.41,
                    "width": 0.05,
                    "color": (255, 150, 100, 180),
                },
                {
                    "start_x": 0.35,
                    "start_y": 0.25,
                    "end_x": 0.65,
                    "end_y": 0.25,
                    "width": 0.08,
                    "color": (255, 100, 100, 255),
                },
            ]
        },
    ],
}

PROBABILITY_CONFIG = {
    "T1": {
        "weight": 3,
        "items": [
            {"type": 0, "id": 0, "unlocked": True},
            {"type": 0, "id": 1, "unlocked": True},
            {"type": 0, "id": 2, "unlocked": True},
            {"type": 0, "id": 3, "unlocked": True},
            {"type": 0, "id": 4, "unlocked": True},
        ],
    },
    "T2": {
        "weight": 5,
        "items": [
            {"type": 1, "id": i, "unlocked": True}
            for i in ATTRIBUTE_MODIFIER_CONFIG.keys()
        ],
    },
    "T3": {
        "weight": 10,
        "items": [
            {"type": 2, "id": i, "unlocked": True}
            for i in PROJECTILE_MODIFIER_CONFIG.keys()
        ],
    },
}

UI_CONFIG = {
    "gun_box_w": 620,
    "gun_box_h": 210,
    "slot_size": 40,
    "info_x": 200,
    "grid_cell_size": 60,
    "grid_cols": 20,
    "grid_rows": 2,
    "inv_bottom_padding": 20,
    "gun_box_padding_x": 50,
    "gun_box_padding_y": 120,
    "gun_box_spacing_y": 270,
}

ENEMY_CONFIG = {
    0: {
        "name": "Chaser",
        "radius": 10,
        "color": (220, 80, 80),
        "image_path": "./Img/enemy_1.png",
        "sprite_height": 56,
        "max_hp": 30,
        "speed": 55,
        "damage": 10,
        "attack_cooldown": 0.8,
        "xp_drop": 1,
        "ai": "chase",
    },
    1: {
        "name": "Runner",
        "radius": 12,
        "color": (220, 220, 80),
        "image_path": "./Img/enemy_2.png",
        "sprite_height": 62,
        "max_hp": 15,
        "speed": 85,
        "damage": 6,
        "attack_cooldown": 0.5,
        "xp_drop": 1,
        "ai": "runner",
    },
    2: {
        "name": "Tank",
        "radius": 30,
        "color": (140, 60, 200),
        "image_path": "./Img/enemy_4.png",
        "sprite_height": 112,
        "max_hp": 200,
        "speed": 40,
        "damage": 25,
        "attack_cooldown": 1.2,
        "xp_drop": 4,
        "ai": "chase",
    },
    3: {
        "name": "Shooter",
        "radius": 16,
        "color": (80, 200, 200),
        "image_path": "./Img/enemy_3.png",
        "sprite_height": 72,
        "max_hp": 35,
        "speed": 90,
        "damage": 8,
        "attack_cooldown": 1.5,
        "xp_drop": 2,
        "ai": "shooter",
        "ranged": True,
        "preferred_distance": 350,
        "bullet_speed": 260,
    },
}

BOSS_CONFIG = {
    "name": "Boss",
    "radius": 60,
    "color": (255, 50, 50),
    "image_path": "./Img/boss_sprite.png",
    "sprite_height": 260,
    "max_hp": 5000,
    "speed": 80,
    "damage": 40,
    "attack_cooldown": 2.0,
    "xp_drop": 50,
    "ai": "boss",
    "ranged": True,
    "bullet_speed": 220,
}

GAME_CONFIG = {
    "boss_spawn_time": 10.0,  # seconds before boss appears (5 minutes)
    "spawn_base_interval": 1.5,
    "spawn_min_interval": 0.25,
    "altar_charge_time": 3.0,
    "altar_buff_amount": {
        "hp": 25,
        "damage": 0.15,
        "speed": 30,
    },
    "xp_pickup_radius": 22,
    "xp_attract_radius": 130,
    "player_max_hp": 100,
    "player_invincible_time": 0.5,
    "xp_per_level_base": 10,
    "card_slot_levels": [10, 20, 30, 40, 50],
}
