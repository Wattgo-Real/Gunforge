from Asset.GameSetting import GAME_CONFIG, PROBABILITY_CONFIG


STAT_UPGRADES = {
    "hp": {
        "label": "Max HP",
        "base_cost": 40,
        "max_level": 10,
        "amount": 20,
        "unit": "+20 HP",
    },
    "damage": {
        "label": "Damage",
        "base_cost": 55,
        "max_level": 10,
        "amount": 0.08,
        "unit": "+8%",
    },
    "speed": {
        "label": "Move Speed",
        "base_cost": 45,
        "max_level": 8,
        "amount": 12,
        "unit": "+12 speed",
    },
}


LEGACY_CARD_UPGRADES = {
    "card_bullet": {
        "label": "Bullet Cards",
        "base_cost": 35,
        "max_level": 3,
        "cards": [(0, 0), (0, 1), (0, 2)],
    },
    "card_attribute": {
        "label": "Attribute Cards",
        "base_cost": 45,
        "max_level": 3,
        "cards": [(1, 5), (1, 15), (1, 25)],
    },
    "card_projectile": {
        "label": "Projectile Cards",
        "base_cost": 55,
        "max_level": 3,
        "cards": [(2, 0), (2, 1), (2, 2)],
    },
    "card_trigger": {
        "label": "Trigger Cards",
        "base_cost": 55,
        "max_level": 3,
        "cards": [(3, 0), (3, 1), (3, 2)],
    },
    "card_multi": {
        "label": "Multibullet Cards",
        "base_cost": 65,
        "max_level": 3,
        "cards": [(4, 0), (4, 1), (4, 2)],
    },
    "card_trajectory": {
        "label": "Trajectory Cards",
        "base_cost": 45,
        "max_level": 3,
        "cards": [(5, 0), (5, 1), (5, 2)],
    },
}


CARD_TYPE_LABELS = {
    0: "Bullet",
    1: "Attribute",
    2: "Projectile",
    3: "Trigger",
    4: "Multibullet",
    5: "Trajectory",
}


def card_key(card_type, card_id):
    return f"{card_type}:{card_id}"


def card_key_to_tuple(key):
    card_type, card_id = key.split(":", 1)
    return int(card_type), int(card_id)


def _build_card_catalog():
    cards = []
    seen = set()
    for tier_name, tier_info in PROBABILITY_CONFIG.items():
        weight = tier_info["weight"]
        for item in tier_info["items"]:
            if not item.get("unlocked", True):
                continue
            key = card_key(item["type"], item["id"])
            if key in seen:
                continue
            seen.add(key)
            cards.append(
                {
                    "key": key,
                    "type": item["type"],
                    "id": item["id"],
                    "tier": tier_name,
                    "cost": 20 + int(weight * 8),
                }
            )
    cards.sort(key=lambda card: (card["type"], card["tier"], card["id"]))
    return tuple(cards)


SHOP_CARD_CATALOG = _build_card_catalog()


def ensure_shop_state(game):
    if not hasattr(game, "shop_upgrades"):
        game.shop_upgrades = {}
    for key in STAT_UPGRADES.keys():
        game.shop_upgrades.setdefault(key, 0)
    if not hasattr(game, "shop_owned_cards"):
        game.shop_owned_cards = set()
    else:
        game.shop_owned_cards = set(game.shop_owned_cards)
    for key, config in LEGACY_CARD_UPGRADES.items():
        owned_count = game.shop_upgrades.get(key, 0)
        for card_type, card_id in config["cards"][:owned_count]:
            game.shop_owned_cards.add(card_key(card_type, card_id))
    if not hasattr(game, "total_points"):
        game.total_points = GAME_CONFIG["initial_points"]


def upgrade_cost(config, level):
    if level >= config["max_level"]:
        return None
    return int(config["base_cost"] * (level + 1))
