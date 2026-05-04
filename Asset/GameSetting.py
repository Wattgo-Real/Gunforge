


COLOR_CONFIG = {
    "cooldown" : (100, 180, 255),
    "reload" : (255, 140, 40),
    "scatter_angel" : (255, 255, 0),
    "capacity" : (100, 255, 100),
}

# Bullet Type: "Type Name", {stats}, {draw_info}
# stats: speed, damage, {attribute_modifier}, info
# draw_info: list of draw_shape (draw_shape: type of shape, {shape_info})
BULLET_CONFIG = {
    0 : [
        "Normal Bullet",
        {
            "speed": 10,
            "damage": 5,
            "info" : "The most basic bullet" 
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.4, "color" : (255, 255, 255, 255)}]
        }
    ],
    1 : [
        "Light Bullet",
        {
            "speed": 5,
            "damage": 3,
            "capacity_modifier" : 20,
            "cooldown_modifier" : -0.1,
            "scatter_angel_modifier" : 5,
            "info" : "High capacity, low damage"
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.3, "color" : (255, 255, 255, 255)}]
        }
    ],
    2 : [
        "Heavy Bullet",
        {
            "speed": 20,
            "damage": 15,
            "capacity_modifier" : -20,
            "cooldown_modifier" : 0.1,
            "scatter_angel_modifier" : -5,
            "info" : "Low capacity, high damage"
        },
        {
            "circle" : [{"pos_x" : 0.5, "pos_y" : 0.5, "size" : 0.5, "color" : (255, 255, 255, 255)}]
        }
    ],
    3 : [
        "Grenades",
        {
            "speed": 3,
            "damage": 10,
            "radius": 40,
            "capacity_modifier" : -20,
            "cooldown_modifier" : 0.5,
            "info" : "Deal damage to enemies in an area. The explosion occurs either when its lifetime ends or when it collides with an enemy or an obstacle."
        }
    ],
    4 : [
        "Laser",
        {
            "speed": 10,
            "damage": 2,
            "scatter_angel_modifier" : -10,
            "info" : "Deals damage to enemies in a straight line."
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

