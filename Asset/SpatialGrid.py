import pygame
import math
from Asset.GameSetting import GRID_CONFIG, ENTITY_TYPE

class SpatialGrid:
    def __init__(self):
        self.cell_w = GRID_CONFIG["cell_w"]
        self.cell_h = GRID_CONFIG["cell_h"]
        self.num_cells_w = GRID_CONFIG["number_of_cells_w"]
        self.num_cells_h = GRID_CONFIG["number_of_cells_h"]
        self.grid = {i : {} for i in range(self.num_cells_w * self.num_cells_h)}

    def clear(self):
        """Clears all cells in the grid."""
        for cell in self.grid.values():
            cell.clear()

    def get_entities_in_cell(self, cell_index):
        """Gets a view of entities in the cell."""
        return self.grid[cell_index].values()

    def contains_entity(self, cell_index, entity_uuid):
        """Checks if an entity is in the cell."""
        return entity_uuid in self.grid[cell_index]

    def insert_entity(self, cell_index, entity):
        """Inserts an entity into the cell."""
        self.grid[cell_index][entity.uuid] = entity

    def remove_entity(self, cell_index, entity_uuid):
        """Removes an entity from the cell if it exists."""
        if entity_uuid in self.grid[cell_index]:
            del self.grid[cell_index][entity_uuid]

    def get_grid_x(self, x):
        """Calculates grid X index with wrapping."""
        return int(x // self.cell_w) % self.num_cells_w

    def get_grid_y(self, y):
        """Calculates grid Y index with wrapping."""
        return int(y // self.cell_h) % self.num_cells_h

    def get_cell_index(self, pos2D):
        """Returns cell index from 2D coordinates."""
        grid_x = self.get_grid_x(pos2D.x)
        grid_y = self.get_grid_y(pos2D.y)
        return grid_y * self.num_cells_w + grid_x

    def register_entity(self, entity):
        """Calculates, sets entity.grid_pos, and inserts it into the grid."""
        grid_pos = self.get_cell_index(entity.pos2D)
        entity.grid_pos = grid_pos
        self.insert_entity(grid_pos, entity)
        return grid_pos

    def update_entity_pos(self, entity, old_grid_pos, new_pos2D):
        """Updates an entity's cell index if its position moves to a new cell."""
        new_grid_pos = self.get_cell_index(new_pos2D)
        if old_grid_pos != new_grid_pos:
            self.remove_entity(old_grid_pos, entity.uuid)
            self.insert_entity(new_grid_pos, entity)
        return new_grid_pos

    def get_entities_near_by_type(self, pos2D, entity_type, range_cells=1):
        """Queries cells in a range_cells neighborhood and returns matching entities."""
        grid_x = self.get_grid_x(pos2D.x)
        grid_y = self.get_grid_y(pos2D.y)
        
        nearby = []
        for i in range(grid_x - range_cells, grid_x + range_cells + 1):
            for j in range(grid_y - range_cells, grid_y + range_cells + 1):
                gx = i % self.num_cells_w
                gy = j % self.num_cells_h
                grid_pos = gy * self.num_cells_w + gx
                for entity in self.grid[grid_pos].values():
                    if entity.entity_type == entity_type:
                        nearby.append(entity)
        return nearby

    def get_entities_in_radius(self, pos2D, radius, entity_type=None):
        """Broadphase cell search for all entities within a physical radius, optionally filtered by type."""
        radius_grid = int(radius // self.cell_w) + 1
        grid_x = self.get_grid_x(pos2D.x)
        grid_y = self.get_grid_y(pos2D.y)
        
        nearby = []
        for i in range(grid_x - radius_grid, grid_x + radius_grid + 1):
            for j in range(grid_y - radius_grid, grid_y + radius_grid + 1):
                gx = i % self.num_cells_w
                gy = j % self.num_cells_h
                grid_pos = gy * self.num_cells_w + gx
                for entity in self.grid[grid_pos].values():
                    if entity_type is not None and entity.entity_type != entity_type:
                        continue
                    nearby.append(entity)
        return nearby

    def register_obstacle(self, obstacle):
        """Multi-cell registration logic for obstacles."""
        half = obstacle.size / 2
        min_gx = int((obstacle.pos2D.x - half.x) // self.cell_w)
        max_gx = int((obstacle.pos2D.x + half.x) // self.cell_w)
        min_gy = int((obstacle.pos2D.y - half.y) // self.cell_h)
        max_gy = int((obstacle.pos2D.y + half.y) // self.cell_h)
        
        obstacle.registered_cells = []
        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                wrapped_gx = gx % self.num_cells_w
                wrapped_gy = gy % self.num_cells_h
                grid_pos = wrapped_gy * self.num_cells_w + wrapped_gx
                if not self.contains_entity(grid_pos, obstacle.uuid):
                    self.insert_entity(grid_pos, obstacle)
                obstacle.registered_cells.append(grid_pos)

    def remove_obstacle(self, obstacle):
        """Multi-cell removal logic for obstacles."""
        for grid_pos in obstacle.registered_cells:
            self.remove_entity(grid_pos, obstacle.uuid)
        obstacle.registered_cells = []


class NoneGrid:
    def __init__(self):
        self.entities = {}
        self.obstacles = {}

    def clear(self):
        self.entities.clear()
        self.obstacles.clear()

    def get_entities_in_cell(self, cell_index):
        return list(self.entities.values()) + list(self.obstacles.values())

    def contains_entity(self, cell_index, entity_uuid):
        return entity_uuid in self.entities

    def insert_entity(self, cell_index, entity):
        self.entities[entity.uuid] = entity

    def remove_entity(self, cell_index, entity_uuid):
        if entity_uuid in self.entities:
            del self.entities[entity_uuid]

    def register_entity(self, entity):
        entity.grid_pos = None
        self.entities[entity.uuid] = entity
        return None

    def update_entity_pos(self, entity, old_grid_pos, new_pos2D):
        return None

    def get_entities_near_by_type(self, pos2D, entity_type, range_cells=1):
        if entity_type == ENTITY_TYPE["obstacle"]:
            return list(self.obstacles.values())
        return [e for e in self.entities.values() if e.entity_type == entity_type]

    def get_entities_in_radius(self, pos2D, radius, entity_type=None):
        source = []
        if entity_type == ENTITY_TYPE["obstacle"]:
            source = self.obstacles.values()
        elif entity_type is not None:
            source = [e for e in self.entities.values() if e.entity_type == entity_type]
        else:
            source = list(self.entities.values()) + list(self.obstacles.values())
            
        return [e for e in source if pos2D.distance_to(e.pos2D) - getattr(e, 'radius', 0) < radius]

    def register_obstacle(self, obstacle):
        obstacle.registered_cells = [None]
        self.obstacles[obstacle.uuid] = obstacle

    def remove_obstacle(self, obstacle):
        if obstacle.uuid in self.obstacles:
            del self.obstacles[obstacle.uuid]
        obstacle.registered_cells = []


class QuadtreeNode:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # pygame.Rect (x, y, width, height)
        self.capacity = capacity  # 該區域最多能容納的物件數量
        self.objects = []         # list of (rect, entity)
        
        # 4 個子節點
        self.north_west = None
        self.north_east = None
        self.south_west = None
        self.south_east = None
        self.is_divided = False   # 紀錄這個區域是否已經被分割了

    def insert(self, rect, entity):
        if not self.boundary.colliderect(rect):
            return False

        if len(self.objects) < self.capacity and not self.is_divided:
            self.objects.append((rect, entity))
            return True

        if not self.is_divided:
            self.subdivide()

        inserted = False
        if self.north_west.insert(rect, entity): inserted = True
        if self.north_east.insert(rect, entity): inserted = True
        if self.south_west.insert(rect, entity): inserted = True
        if self.south_east.insert(rect, entity): inserted = True

        return inserted

    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width, self.boundary.height
        half_w = w / 2
        half_h = h / 2

        self.north_west = QuadtreeNode(pygame.Rect(x, y, half_w, half_h), self.capacity)
        self.north_east = QuadtreeNode(pygame.Rect(x + half_w, y, half_w, half_h), self.capacity)
        self.south_west = QuadtreeNode(pygame.Rect(x, y + half_h, half_w, half_h), self.capacity)
        self.south_east = QuadtreeNode(pygame.Rect(x + half_w, y + half_h, half_w, half_h), self.capacity)

        self.is_divided = True

        for rect, entity in self.objects:
            self.north_west.insert(rect, entity)
            self.north_east.insert(rect, entity)
            self.south_west.insert(rect, entity)
            self.south_east.insert(rect, entity)
        self.objects.clear()

    def query_range(self, range_rect, found_list):
        if not self.boundary.colliderect(range_rect):
            return

        for rect, entity in self.objects:
            if range_rect.colliderect(rect):
                found_list.append(entity)

        if self.is_divided:
            self.north_west.query_range(range_rect, found_list)
            self.north_east.query_range(range_rect, found_list)
            self.south_west.query_range(range_rect, found_list)
            self.south_east.query_range(range_rect, found_list)


class Quadtree:
    def __init__(self):
        self.entities = {}
        self.obstacles = {}
        self.dirty = True
        self.root = None
        self.width = GRID_CONFIG["cell_w"] * GRID_CONFIG["number_of_cells_w"]
        self.height = GRID_CONFIG["cell_h"] * GRID_CONFIG["number_of_cells_h"]

    def clear(self):
        self.entities.clear()
        self.obstacles.clear()
        self.dirty = True
        self.root = None

    def get_entities_in_cell(self, cell_index):
        return list(self.entities.values()) + list(self.obstacles.values())

    def contains_entity(self, cell_index, entity_uuid):
        return entity_uuid in self.entities

    def insert_entity(self, cell_index, entity):
        self.entities[entity.uuid] = entity
        self.dirty = True

    def remove_entity(self, cell_index, entity_uuid):
        if entity_uuid in self.entities:
            del self.entities[entity_uuid]
            self.dirty = True

    def register_entity(self, entity):
        entity.grid_pos = None
        self.entities[entity.uuid] = entity
        self.dirty = True
        return None

    def update_entity_pos(self, entity, old_grid_pos, new_pos2D):
        self.dirty = True
        return None

    def register_obstacle(self, obstacle):
        obstacle.registered_cells = [None]
        self.obstacles[obstacle.uuid] = obstacle
        self.dirty = True

    def remove_obstacle(self, obstacle):
        if obstacle.uuid in self.obstacles:
            del self.obstacles[obstacle.uuid]
            self.dirty = True
        obstacle.registered_cells = []

    def get_boundary_rect_wrapped(self, entity):
        wx = entity.pos2D.x % self.width
        wy = entity.pos2D.y % self.height
        if hasattr(entity, 'size'):
            half = entity.size / 2
            return pygame.Rect(wx - half.x, wy - half.y, entity.size.x, entity.size.y)
        else:
            radius = getattr(entity, 'radius', 0)
            return pygame.Rect(wx - radius, wy - radius, radius * 2, radius * 2)

    def _rebuild_tree(self):
        boundary = pygame.Rect(0, 0, self.width, self.height)
        self.root = QuadtreeNode(boundary, capacity=4)
        
        for entity in self.entities.values():
            rect = self.get_boundary_rect_wrapped(entity)
            self.root.insert(rect, entity)
            
        for obs in self.obstacles.values():
            rect = self.get_boundary_rect_wrapped(obs)
            self.root.insert(rect, obs)
            
        self.dirty = False

    def query_wrapped(self, center_x, center_y, w, h):
        cx = center_x % self.width
        cy = center_y % self.height
        
        rects = []
        rects.append(pygame.Rect(cx - w/2, cy - h/2, w, h))
        
        if cx - w/2 < 0:
            rects.append(pygame.Rect(cx - w/2 + self.width, cy - h/2, w, h))
        if cx + w/2 > self.width:
            rects.append(pygame.Rect(cx - w/2 - self.width, cy - h/2, w, h))
        if cy - h/2 < 0:
            rects.append(pygame.Rect(cx - w/2, cy - h/2 + self.height, w, h))
        if cy + h/2 > self.height:
            rects.append(pygame.Rect(cx - w/2, cy - h/2 - self.height, w, h))
            
        if (cx - w/2 < 0) and (cy - h/2 < 0):
            rects.append(pygame.Rect(cx - w/2 + self.width, cy - h/2 + self.height, w, h))
        if (cx + w/2 > self.width) and (cy - h/2 < 0):
            rects.append(pygame.Rect(cx - w/2 - self.width, cy - h/2 + self.height, w, h))
        if (cx - w/2 < 0) and (cy + h/2 > self.height):
            rects.append(pygame.Rect(cx - w/2 + self.width, cy - h/2 - self.height, w, h))
        if (cx + w/2 > self.width) and (cy + h/2 > self.height):
            rects.append(pygame.Rect(cx - w/2 - self.width, cy - h/2 - self.height, w, h))
            
        results = []
        seen_uuids = set()
        for r in rects:
            found = []
            if self.root:
                self.root.query_range(r, found)
            for entity in found:
                if entity.uuid not in seen_uuids:
                    seen_uuids.add(entity.uuid)
                    results.append(entity)
        return results

    def get_entities_near_by_type(self, pos2D, entity_type, range_cells=1):
        if self.dirty:
            self._rebuild_tree()
            
        cell_w = self.width / GRID_CONFIG["number_of_cells_w"]
        cell_h = self.height / GRID_CONFIG["number_of_cells_h"]
        query_w = (2 * range_cells + 1) * cell_w
        query_h = (2 * range_cells + 1) * cell_h
        
        entities = self.query_wrapped(pos2D.x, pos2D.y, query_w, query_h)
        return [e for e in entities if getattr(e, 'entity_type', None) == entity_type]

    def get_entities_in_radius(self, pos2D, radius, entity_type=None):
        if self.dirty:
            self._rebuild_tree()
            
        query_size = 2 * radius
        entities = self.query_wrapped(pos2D.x, pos2D.y, query_size, query_size)
        
        results = []
        for e in entities:
            if entity_type is not None and getattr(e, 'entity_type', None) != entity_type:
                continue
            if pos2D.distance_to(e.pos2D) - getattr(e, 'radius', 0) < radius:
                results.append(e)
        return results