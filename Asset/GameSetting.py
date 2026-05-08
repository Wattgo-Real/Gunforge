


COLOR_CONFIG = {
    "cooldown" : (100, 180, 255),
    "reload" : (255, 140, 40),
    "scatter_angel" : (255, 255, 0),
    "capacity" : (100, 255, 100),
    "phy_damage" : (255, 255, 255),
    "exp_damage" : (255, 100, 0),
    "bur_damage" : (255, 200, 0),
    "speed" : (100, 255, 150)
}

# Bullet Type: "Type Name", {stats}, {draw_info}
# stats: speed, damage, {attribute_modifier}, info
# draw_info: list of draw_shape (draw_shape: type of shape, {shape_info})
BULLET_CONFIG = {
    0 : [
        "Normal Bullet",
        {
            "speed": 300,
            "physical_damage": 5,
            "info" : "The most basic bullet, deal physical damage" ,
            "draw_info" : {"circle" : [{"radius" : 3, "color" : (255, 255, 255, 255)}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.4, "color" : (255, 255, 255, 255)}]
        }
    ],
    1 : [
        "Light Bullet",
        {
            "speed": 150,
            "physical_damage": 3,
            "capacity_modifier" : 20,
            "cooldown_modifier" : -0.1,
            "scatter_angel_modifier" : 5,
            "info" : "Deal physical damage with high capacity, low speed, low damage and narrow scatter angle",
            "draw_info" : {"circle" : [{"radius" : 2, "color" : (255, 255, 255, 255)}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.3, "color" : (255, 255, 255, 255)}]
        }
    ],
    2 : [
        "Heavy Bullet",
        {
            "speed": 600,
            "physical_damage": 15,
            "capacity_modifier" : -20,
            "cooldown_modifier" : 0.1,
            "scatter_angel_modifier" : -5,
            "info" : "Deal physical damage with low capacity, high speed, high damage and wide scatter angle",
            "draw_info" : {"circle" : [{"radius" : 4, "color" : (255, 255, 255, 255)}]}
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.5, "color" : (255, 255, 255, 255)}]
        }
    ],
    3 : [
        "Grenades",
        {
            "speed": 100,
            "explosion_damage": 10,
            "radius": 40,
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
            "speed": 300,
            "burn_damage": 2,
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
        "Add Cooldown",
        {
            "cooldown_modifier" : 0.1,
            "info" : "Add cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]}],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    1 : [
        "Sub Cooldown",
        {
            "cooldown_modifier" : -0.1,
            "info" : "Subtract cooldown"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["cooldown"]}],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    2 : [
        "Add Reload",
        {
            "reload_modifier" : 0.5,
            "info" : "Add reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    3 : [
        "Sub Reload",
        {
            "reload_modifier" : -0.5,
            "info" : "Subtract reload"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["reload"]}],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    4 : [
        "Add Scatter Angel",
        {
            "scatter_angel_modifier" : 5,
            "info" : "Add scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    5 : [
        "Sub Scatter Angel",
        {
            "scatter_angel_modifier" : -5,
            "info" : "Subtract scatter angel"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["scatter_angel"]}],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    6 : [
        "Add Capacity",
        {
            "capacity_modifier" : 5,
            "info" : "Add capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ],
    7 : [
        "Sub Capacity",
        {
            "capacity_modifier" : -5,
            "info" : "Subtract capacity"
        },
        {
            "line" : [{"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.40, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]},
                     {"start_x" : 0.60, "start_y" : 0.65, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.05, "color" : COLOR_CONFIG["capacity"]}],
            #"string" : [{"text" : "+", "font" : "Arial", "pos_x" : 0.3, "pos_y" : 0.3, "size" : 0.4, "color" : (255, 255, 255, 255)}],
        }
    ]
}

EFFECT_MODIFIER_CONFIG = {
    0 : [
        "Speed ​​damage bonus",
        { 
            "info" : "Physical damage is modified by adding half of the bullet’s final velocity value, and each bullet can only receive this bonus once."
        },
        {
            "circle" : [{"pos_x" : 0.25, "pos_y" : 0.50, "size" : 0.20, "color" : (255,255,255,255)}],
            "line" : [{"start_x" : 0.15, "start_y" : 0.40, "end_x" : 0.35, "end_y" : 0.60, "width" : 0.05, "color" : (255,255,255,255)},
                     {"start_x" : 0.15, "start_y" : 0.60, "end_x" : 0.35, "end_y" : 0.40, "width" : 0.05, "color" : (255,255,255,255)},
                     {"start_x" : 0.70, "start_y" : 0.30, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.15, "color" : COLOR_CONFIG["speed"]},
                     {"start_x" : 0.70, "start_y" : 0.70, "end_x" : 0.80, "end_y" : 0.50, "width" : 0.15, "color" : COLOR_CONFIG["speed"]},

                     {"start_x" : 0.50, "start_y" : 0.25, "end_x" : 0.50, "end_y" : 0.75, "width" : 0.025, "color" : (255,255,255,255)},
                     {"start_x" : 0.40, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.025, "color" : (255,255,255,255)},
                     {"start_x" : 0.60, "start_y" : 0.35, "end_x" : 0.50, "end_y" : 0.25, "width" : 0.025, "color" : (255,255,255,255)}],
        }
    ],
    10 : [
        "Split",
        { 
            "info" : "aa"
        },
        {
            "circle" : [{"pos_x" : 0.50, "pos_y" : 0.75, "size" : 0.15, "color" : (200, 200, 200, 255)}],
            "line" : [{"start_x" : 0.50, "start_y" : 0.75, "end_x" : 0.25, "end_y" : 0.25, "width" : 0.05, "color" : (255, 255, 255, 255)},
                     {"start_x" : 0.50, "start_y" : 0.75, "end_x" : 0.75, "end_y" : 0.25, "width" : 0.05, "color" : (255, 255, 255, 255)},
                     {"start_x" : 0.25, "start_y" : 0.25, "end_x" : 0.20, "end_y" : 0.40, "width" : 0.03, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.25, "start_y" : 0.25, "end_x" : 0.40, "end_y" : 0.30, "width" : 0.03, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.75, "start_y" : 0.25, "end_x" : 0.80, "end_y" : 0.40, "width" : 0.03, "color" : (200, 200, 200, 255)},
                     {"start_x" : 0.75, "start_y" : 0.25, "end_x" : 0.60, "end_y" : 0.30, "width" : 0.03, "color" : (200, 200, 200, 255)}],
        }
    ],
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
    "gun_box_padding_y": 50,
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
    "xp_per_level_base" : 10,
    "card_slot_levels" : [10, 20, 30, 40, 50],
}

