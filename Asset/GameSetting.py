


ENTITY_TYPE = {
    "bullet" : 0,
    "enemy" : 1,
    "player" : 2,
    "obstacle" : 3,
}

GRID_CONFIG = {
    "cell_w" : 40,
    "cell_h" : 40,
    "number_of_cells_w" : 50,
    "number_of_cells_h" : 50,
}

COLOR_CONFIG = {
    "cooldown" : (100, 180, 255),
    "reload" : (255, 140, 40),
    "scatter_angel" : (255, 255, 0),
    "capacity" : (100, 255, 100),
    "phy_damage" : (255, 255, 255),
    "exp_damage" : (255, 100, 0),
    "bur_damage" : (255, 200, 0),
    "speed" : (100, 255, 150),
    "normal_bullet" : (200, 200, 150, 255),
    "enemy" : (255, 0, 0, 255),
}

# Bullet Type: "Type Name", {stats}, {draw_info}
# stats: speed, damage, {attribute_modifier}, info
# draw_info: list of draw_shape (draw_shape: type of shape, {shape_info})
BULLET_CONFIG = {
    0 : [
        "Normal Bullet",
        {
            "speed": 10,
            "physical_damage": 5,
            "radius" : 3,
            "info" : "The most basic bullet, deal physical damage" ,
            "draw_info" : {"circle" : [{"radius" : 3, "color" : COLOR_CONFIG["normal_bullet"]}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.4, "color" : COLOR_CONFIG["normal_bullet"]}]
        }
    ],
    1 : [
        "Light Bullet",
        {
            "speed": 5,
            "physical_damage": 3,
            "radius" : 2,
            "capacity_modifier" : 20,
            "cooldown_modifier" : -0.1,
            "scatter_angel_modifier" : 5,
            "info" : "Deal physical damage with high capacity, low speed, low damage and narrow scatter angle",
            "draw_info" : {"circle" : [{"radius" : 2, "color" : COLOR_CONFIG["normal_bullet"]}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.3, "color" : COLOR_CONFIG["normal_bullet"]}]
        }
    ],
    2 : [
        "Heavy Bullet",
        {
            "speed": 20,
            "physical_damage": 15,
            "radius" : 4,
            "capacity_modifier" : -20,
            "cooldown_modifier" : 0.1,
            "scatter_angel_modifier" : -5,
            "info" : "Deal physical damage with low capacity, high speed, high damage and wide scatter angle",
            "draw_info" : {"circle" : [{"radius" : 4, "color" : COLOR_CONFIG["normal_bullet"]}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.5, "color" : COLOR_CONFIG["normal_bullet"]}]
        }
    ],
    3 : [
        "Grenades",
        {
            "speed": 4,
            "explosion_damage": 10,
            "radius": 5,
            "explosion_radius": 80,
            "capacity_modifier" : -20,
            "cooldown_modifier" : 0.5,
            "info" : "Deal explosion damage to enemies in an area. The explosion occurs either when its lifetime ends or when it collides with an enemy or an obstacle.",
            "draw_info" : {"circle" : [{"radius" : 5, "color" : (50, 50, 50, 255)},
                                        {"radius" : 4, "color" : (100, 100, 100, 255)}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.6, "color" : (50, 50, 50, 255)},
                        {"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.5, "color" : (100, 100, 100, 255)}],
            "line" : [{"start_x" : 0.65, "start_y" : 0.3, "end_x" : 0.77, "end_y" : 0.18, "width" : 0.05, "color" : (100, 100, 100, 255)}]
        }
    ],
    4 : [
        "Laser",
        {
            "speed": 10,
            "burn_damage": 2,
            "radius": 2,
            "scatter_angel_modifier" : -10,
            "info" : "Deals burn damage to enemies in a straight line.",
            "draw_info" : {"line" : [{"width" : 2, "color" : (150, 255, 120, 255)}]}
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.15, "end_x" : 0.5, "end_y" : 0.85, "width" : 0.3, "color" : (150, 255, 120, 255)},
                        {"start_x" : 0.50, "start_y" : 0.15, "end_x" : 0.5, "end_y" : 0.85, "width" : 0.2, "color" : (255, 255, 255, 255)}]
        }
    ]
}


ATTRIBUTE_MODIFIER_CONFIG = {
    0 : [
        "Add Cooldown I",
        {
            "cooldown_modifier" : 0.1,
            "info" : "Add cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    1 : [
        "Add Cooldown II",
        {
            "cooldown_modifier" : 0.2,
            "info" : "Add cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    2 : [
        "Add Cooldown III",
        {
            "cooldown_modifier" : 0.3,
            "info" : "Add cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    3 : [
        "Add Cooldown IV",
        {
            "cooldown_modifier" : 0.4,
            "info" : "Add cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    4 : [
        "Add Cooldown V",
        {
            "cooldown_modifier" : 0.5,
            "info" : "Add cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    5 : [
        "Sub Cooldown I",
        {
            "cooldown_modifier" : -0.1,
            "info" : "Subtract cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    6 : [
        "Sub Cooldown II",
        {
            "cooldown_modifier" : -0.2,
            "info" : "Subtract cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    7 : [
        "Sub Cooldown III",
        {
            "cooldown_modifier" : -0.3,
            "info" : "Subtract cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    8 : [
        "Sub Cooldown IV",
        {
            "cooldown_modifier" : -0.4,
            "info" : "Subtract cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    9 : [
        "Sub Cooldown V",
        {
            "cooldown_modifier" : -0.5,
            "info" : "Subtract cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["cooldown"]}],
        }
    ],
    10 : [
        "Add Reload I",
        {
            "reload_modifier" : 0.2,
            "info" : "Add reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},],
        }
    ],
    11 : [
        "Add Reload II",
        {
            "reload_modifier" : 0.5,
            "info" : "Add reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["reload"]},],
        }
    ],
    12 : [
        "Add Reload III",
        {
            "reload_modifier" : 1.0,
            "info" : "Add reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["reload"]},],
        }
    ],
    13 : [
        "Add Reload IV",
        {
            "reload_modifier" : 1.5,
            "info" : "Add reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["reload"]},],
        }
    ],
    14 : [
        "Add Reload V",
        {
            "reload_modifier" : 2.5,
            "info" : "Add reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["reload"]},],
        }
    ],
    15 : [
        "Sub Reload I",
        {
            "reload_modifier" : -0.2,
            "info" : "Subtract reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]}],
        }
    ],
    16 : [
        "Sub Reload II",
        {
            "reload_modifier" : -0.5,
            "info" : "Subtract reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["reload"]}],
        }
    ],
    17 : [
        "Sub Reload III",
        {
            "reload_modifier" : -1.0,
            "info" : "Subtract reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["reload"]}],
        }
    ],
    18 : [
        "Sub Reload IV",
        {
            "reload_modifier" : -1.5,
            "info" : "Subtract reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["reload"]}],
        }
    ],
    19 : [
        "Sub Reload V",
        {
            "reload_modifier" : -2.5,
            "info" : "Subtract reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["reload"]}],
        }
    ],
    20 : [
        "Add Scatter Angel I",
        {
            "scatter_angel_modifier" : 5,
            "info" : "Add scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},],
        }
    ],
    21 : [
        "Add Scatter Angel II",
        {
            "scatter_angel_modifier" : 10,
            "info" : "Add scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["scatter_angel"]},],
        }
    ],
    22 : [
        "Add Scatter Angel III",
        {
            "scatter_angel_modifier" : 15,
            "info" : "Add scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["scatter_angel"]},],
        }
    ],
    23 : [
        "Add Scatter Angel IV",
        {
            "scatter_angel_modifier" : 20,
            "info" : "Add scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["scatter_angel"]},],
        }
    ],
    24 : [
        "Add Scatter Angel V",
        {
            "scatter_angel_modifier" : 30,
            "info" : "Add scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["scatter_angel"]},],
        }
    ],
    25 : [
        "Sub Scatter Angel I",
        {
            "scatter_angel_modifier" : -5,
            "info" : "Subtract scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]}],
        }
    ],
    26 : [
        "Sub Scatter Angel II",
        {
            "scatter_angel_modifier" : -10,
            "info" : "Subtract scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["scatter_angel"]}],
        }
    ],
    27 : [
        "Sub Scatter Angel III",
        {
            "scatter_angel_modifier" : -15,
            "info" : "Subtract scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["scatter_angel"]}],
        }
    ],
    28 : [
        "Sub Scatter Angel IV",
        {
            "scatter_angel_modifier" : -20,
            "info" : "Subtract scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["scatter_angel"]}],
        }
    ],
    29 : [
        "Sub Scatter Angel V",
        {
            "scatter_angel_modifier" : -30,
            "info" : "Subtract scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["scatter_angel"]}],
        }
    ],
    30 : [
        "Add Capacity I",
        {
            "capacity_modifier" : 5,
            "info" : "Add capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},],
        }
    ],
    31 : [
        "Add Capacity II",
        {
            "capacity_modifier" : 10,
            "info" : "Add capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.1, "color" : COLOR_CONFIG["capacity"]},],
        }
    ],
    32 : [
        "Add Capacity III",
        {
            "capacity_modifier" : 15,
            "info" : "Add capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.15, "color" : COLOR_CONFIG["capacity"]},],
        }
    ],
    33 : [
        "Add Capacity IV",
        {
            "capacity_modifier" : 20,
            "info" : "Add capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.2, "color" : COLOR_CONFIG["capacity"]},],
        }
    ],
    34 : [
        "Add Capacity V",
        {
            "capacity_modifier" : 30,
            "info" : "Add capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.25, "color" : COLOR_CONFIG["capacity"]},],
        }
    ],
    35 : [
        "Sub Capacity I",
        {
            "capacity_modifier" : -5,
            "info" : "Subtract capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]}],
        }
    ],
    36 : [
        "Sub Capacity II",
        {
            "capacity_modifier" : -10,
            "info" : "Subtract capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.1, "color" : COLOR_CONFIG["capacity"]}],
        }
    ],
    37 : [
        "Sub Capacity III",
        {
            "capacity_modifier" : -15,
            "info" : "Subtract capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.15, "color" : COLOR_CONFIG["capacity"]}],
        }
    ],
    38 : [
        "Sub Capacity IV",
        {
            "capacity_modifier" : -20,
            "info" : "Subtract capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.2, "color" : COLOR_CONFIG["capacity"]}],
        }
    ],
    39 : [
        "Sub Capacity V",
        {
            "capacity_modifier" : -30,
            "info" : "Subtract capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.25, "color" : COLOR_CONFIG["capacity"]}],
        }
    ],


    50 : [
        "Add Speed I",
        {
            "bullet_speed_modifier" : 3,
            "info" : "Add bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    51 : [
        "Add Speed II",
        {
            "bullet_speed_modifier" : 6,
            "info" : "Add bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    52 : [
        "Add Speed III",
        {
            "bullet_speed_modifier" : 10,
            "info" : "Add bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.15, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.15, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    53 : [
        "Add Speed IV",
        {
            "bullet_speed_modifier" : 15,
            "info" : "Add bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.2, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.2, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    54 : [
        "Add Speed V",
        {
            "bullet_speed_modifier" : 25,
            "info" : "Add bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.25, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.25, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    55 : [
        "Sub Speed I",
        {
            "bullet_speed_modifier" : -3,
            "info" : "Subtract bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    56 : [
        "Sub Speed II",
        {
            "bullet_speed_modifier" : -6,
            "info" : "Subtract bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    57 : [
        "Sub Speed III",
        {
            "bullet_speed_modifier" : -10,
            "info" : "Subtract bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.15, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.15, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    58 : [
        "Sub Speed IV",
        {
            "bullet_speed_modifier" : -15,
            "info" : "Subtract bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.2, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.2, "color" : COLOR_CONFIG["speed"]}],
        }
    ],
    59 : [
        "Sub Speed V",
        {
            "bullet_speed_modifier" : -25,
            "info" : "Subtract bullet speed"
        },
        {
            "line" : [{"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.25, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.40, "start_y" : 0.70, "end_x" : 0.60, "end_y" : 0.50, "width" : 0.25, "color" : COLOR_CONFIG["speed"]}],
        }
    ],

    100 : [
        "Speed damage bonus",
        { 
            "reload_modifier" : 0.2,
            "info" : "Bullet’s Physical damage is modified by adding half of the bullet’s speed value, and each bullet can only receive this bonus once."
        },
        {
            "circle" : [{"pos_x" : 0.25, "pos_y" : 0.50, "size" : 0.20, "color" : COLOR_CONFIG["phy_damage"]}],
            "line" : [{"start_x" : 0.15, "start_y" : 0.40, "end_x" : 0.35, "end_y" : 0.60, "width" : 0.1, "color" : COLOR_CONFIG["phy_damage"]},
                     {"start_x" : 0.15, "start_y" : 0.60, "end_x" : 0.35, "end_y" : 0.40, "width" : 0.1, "color" : COLOR_CONFIG["phy_damage"]},
                     {"start_x" : 0.70, "start_y" : 0.30, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.70, "start_y" : 0.70, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]},

                     {"start_x" : 0.50, "start_y" : 0.20, "end_x" : 0.50, "end_y" : 0.80, "width" : 0.05, "color" : (255,255,255,255)},
                     {"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.50, "end_y" : 0.20, "width" : 0.05, "color" : (255,255,255,255)},
                     {"start_x" : 0.60, "start_y" : 0.30, "end_x" : 0.50, "end_y" : 0.20, "width" : 0.05, "color" : (255,255,255,255)}],
        }
    ],
    101 : [
        "Damage Speed bonus",
        {
            "reload_modifier" : 0.2,
            "info" : "Bullet’s speed is modified by adding half of the bullet’s Physical damage value, and each bullet can only receive this bonus once."
        },
        {
            "circle" : [{"pos_x" : 0.75, "pos_y" : 0.50, "size" : 0.20, "color" : COLOR_CONFIG["phy_damage"]}],
            "line" : [{"start_x" : 0.85, "start_y" : 0.40, "end_x" : 0.65, "end_y" : 0.60, "width" : 0.1, "color" : COLOR_CONFIG["phy_damage"]},
                     {"start_x" : 0.85, "start_y" : 0.60, "end_x" : 0.65, "end_y" : 0.40, "width" : 0.1, "color" : COLOR_CONFIG["phy_damage"]},
                     {"start_x" : 0.20, "start_y" : 0.30, "end_x" : 0.30, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.20, "start_y" : 0.70, "end_x" : 0.30, "end_y" : 0.50, "width" : 0.1, "color" : COLOR_CONFIG["speed"]},

                     {"start_x" : 0.50, "start_y" : 0.20, "end_x" : 0.50, "end_y" : 0.80, "width" : 0.05, "color" : (255,255,255,255)},
                     {"start_x" : 0.40, "start_y" : 0.30, "end_x" : 0.50, "end_y" : 0.20, "width" : 0.05, "color" : (255,255,255,255)},
                     {"start_x" : 0.60, "start_y" : 0.30, "end_x" : 0.50, "end_y" : 0.20, "width" : 0.05, "color" : (255,255,255,255)}],
        }
    ],
}

EFFECT_MODIFIER_CONFIG = {
    0 : [
        "F Split",
        { 
            "info" : "After the condition is triggered, the bullet will split into 2 bullets (±45 degrees), dealing half damage.",
            "default_trigger" : "hit"
        },
        {
            "circle" : [{"pos_x" : 0.50, "pos_y" : 0.65, "size" : 0.3, "color" : COLOR_CONFIG["normal_bullet"]}],
            "line" : [{"start_x" : 0.50, "start_y" : 0.75, "end_x" : 0.50, "end_y" : 0.95, "width" : 0.05, "color" : COLOR_CONFIG["normal_bullet"]},
                     {"start_x" : 0.50, "start_y" : 0.65, "end_x" : 0.25, "end_y" : 0.25, "width" : 0.05, "color" : (255, 255, 255, 255)},
                     {"start_x" : 0.50, "start_y" : 0.65, "end_x" : 0.75, "end_y" : 0.25, "width" : 0.05, "color" : (255, 255, 255, 255)},
                     {"start_x" : 0.25, "start_y" : 0.25, "end_x" : 0.20, "end_y" : 0.40, "width" : 0.05, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.25, "start_y" : 0.25, "end_x" : 0.40, "end_y" : 0.30, "width" : 0.05, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.75, "start_y" : 0.25, "end_x" : 0.80, "end_y" : 0.40, "width" : 0.05, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.75, "start_y" : 0.25, "end_x" : 0.60, "end_y" : 0.30, "width" : 0.05, "color" : (200, 200, 200, 255)}],
        }
    ],
    1 : [
        "B Split",
        { 
            "info" : "After the condition is triggered, the bullet will split into 2 bullets (±135 degrees), dealing half damage.",
            "default_trigger" : "hit"
        },
        {
            "circle" : [{"pos_x" : 0.50, "pos_y" : 0.35, "size" : 0.3, "color" : COLOR_CONFIG["normal_bullet"]}],
            "line" : [{"start_x" : 0.50, "start_y" : 0.45, "end_x" : 0.50, "end_y" : 0.65, "width" : 0.05, "color" : COLOR_CONFIG["normal_bullet"]},
                     {"start_x" : 0.50, "start_y" : 0.35, "end_x" : 0.25, "end_y" : 0.75, "width" : 0.05, "color" : (255, 255, 255, 255)},
                     {"start_x" : 0.50, "start_y" : 0.35, "end_x" : 0.75, "end_y" : 0.75, "width" : 0.05, "color" : (255, 255, 255, 255)},
                     {"start_x" : 0.25, "start_y" : 0.75, "end_x" : 0.20, "end_y" : 0.60, "width" : 0.05, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.25, "start_y" : 0.75, "end_x" : 0.40, "end_y" : 0.70, "width" : 0.05, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.75, "start_y" : 0.75, "end_x" : 0.80, "end_y" : 0.60, "width" : 0.05, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.75, "start_y" : 0.75, "end_x" : 0.60, "end_y" : 0.70, "width" : 0.05, "color" : (200, 200, 200, 255)}],
        }
    ],
    2 : [
        "Penetrate",
        { 
            "info" : "The bullet can penetrate through enemies one additional time.",
        },
        {
            "circle" : [{"pos_x" : 0.50, "pos_y" : 0.5, "size" : 0.3, "color" : COLOR_CONFIG["enemy"]}],
            "line" : [{"start_x" : 0.20, "start_y" : 0.50, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["normal_bullet"]},
                     {"start_x" : 0.70, "start_y" : 0.40, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["normal_bullet"]},
                     {"start_x" : 0.70, "start_y" : 0.60, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.05, "color" : COLOR_CONFIG["normal_bullet"]}]
        }
    ],
    3 : [
        "Bounce",
        { 
            "info" : "The bullet can bounce off enemies and walls one additional time.",
        },
        {
            "circle" : [{"pos_x" : 0.50, "pos_y" : 0.70, "size" : 0.2, "color" : COLOR_CONFIG["normal_bullet"]}],
            "line" : [{"start_x" : 0.15, "start_y" : 0.75, "end_x" : 0.85, "end_y" : 0.75, "width" : 0.08, "color" : (150, 150, 150, 255)},
                      {"start_x" : 0.25, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.70, "width" : 0.05, "color" : COLOR_CONFIG["normal_bullet"]},
                      {"start_x" : 0.50, "start_y" : 0.70, "end_x" : 0.75, "end_y" : 0.35, "width" : 0.05, "color" : (255, 255, 255, 255)},
                      {"start_x" : 0.75, "start_y" : 0.35, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.05, "color" : (200, 200, 200, 255)},
                      {"start_x" : 0.75, "start_y" : 0.35, "end_x" : 0.60, "end_y" : 0.40, "width" : 0.05, "color" : (200, 200, 200, 255)}]
        }
    ],
}

PROBABILITY_CONFIG = {
    "T1" : {"weight" : 3,"items" : [
        {"type" : 0, "id" : 0, "unlocked" : True},
        {"type" : 0, "id" : 1, "unlocked" : True},
        {"type" : 0, "id" : 2, "unlocked" : True},
        {"type" : 0, "id" : 3, "unlocked" : True},
        {"type" : 0, "id" : 4, "unlocked" : True},
    ]},
    "T2" : {"weight" : 5 ,"items" : [
        {"type" : 1, "id" : i, "unlocked" : True} for i in ATTRIBUTE_MODIFIER_CONFIG.keys()
    ]},
    "T3" : {"weight" : 10 ,"items" : [
        {"type" : 2, "id" : i, "unlocked" : True} for i in EFFECT_MODIFIER_CONFIG.keys()
    ]},
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
    0 : {
        "name" : "Chaser",
        "radius" : 18,
        "color" : (220, 80, 80),
        "max_hp" : 30,
        "speed" : 110,
        "damage" : 10,
        "attack_cooldown" : 0.8,
        "xp_drop" : 1,
        "ai" : "chase",
    },
    1 : {
        "name" : "Runner",
        "radius" : 12,
        "color" : (220, 220, 80),
        "max_hp" : 15,
        "speed" : 170,
        "damage" : 6,
        "attack_cooldown" : 0.5,
        "xp_drop" : 1,
        "ai" : "runner",
    },
    2 : {
        "name" : "Tank",
        "radius" : 30,
        "color" : (140, 60, 200),
        "max_hp" : 200,
        "speed" : 60,
        "damage" : 25,
        "attack_cooldown" : 1.2,
        "xp_drop" : 4,
        "ai" : "chase",
    },
    3 : {
        "name" : "Shooter",
        "radius" : 16,
        "color" : (80, 200, 200),
        "max_hp" : 35,
        "speed" : 90,
        "damage" : 8,
        "attack_cooldown" : 1.5,
        "xp_drop" : 2,
        "ai" : "shooter",
        "ranged" : True,
        "preferred_distance" : 350,
        "bullet_speed" : 260,
    },
}

BOSS_CONFIG = {
    "name" : "Boss",
    "radius" : 60,
    "color" : (255, 50, 50),
    "max_hp" : 5000,
    "speed" : 80,
    "damage" : 40,
    "attack_cooldown" : 2.0,
    "xp_drop" : 50,
    "ai" : "boss",
    "ranged" : True,
    "bullet_speed" : 220,
}

GAME_CONFIG = {
    "boss_spawn_time" : 300.0,    # seconds before boss appears (5 minutes)
    "spawn_base_interval" : 1.5,
    "spawn_min_interval" : 0.25,
    "altar_charge_time" : 3.0,
    "altar_buff_amount" : {
        "hp" : 25,
        "damage" : 0.15,
        "speed" : 30,
    },
    "xp_pickup_radius" : 22,
    "xp_attract_radius" : 130,
    "player_max_hp" : 100,
    "player_invincible_time" : 0.5,
    "xp_per_level_base" : 1,
    "card_slot_levels" : [10, 20, 30, 40, 50],
}

