import tkinter as tk
import random

class Mob:
    def __init__(self, x, y, name, mob_type, faction=None, parents=None, health=100, job="civilian"):
        self.x = x
        self.y = y
        self.name = name
        self.mob_type = mob_type  # "Human", "Bear", or "Zombie"
        self.faction = faction
        self.age = 0
        self.age_ticks = 0
        self.neutral_ticks = 0
        self.parents = parents or []
        self.children = []
        self.health = health
        self.is_king = False
        self.job = job  # "civilian", "guard", "warrior", "bear", or "zombie"
        self.kills = 0
        self.under_attack = False
        self.alerted = False  # Warriors alerted to assist
        self.target_attack_pos = None
        self.fertility_meter = 0
        self.fertility_ticks = 0
        self.children_count = 0
        self.max_children = random.randint(1, 3)

class GreenGridGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Green Grid Faction Simulation")

        self.grid_size = 100
        self.cell_size = 5
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size

        window_width = self.canvas_width + 400
        window_height = self.canvas_height + int(self.canvas_height * 0.25)
        self.geometry(f"{window_width}x{window_height}")

        # Basic setup
        self.grid_size = 100
        self.cell_size = 5
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        window_width = self.canvas_width + 400  # for side panels
        window_height = self.canvas_height + int(self.canvas_height * 0.25)
        self.geometry(f"{window_width}x{window_height}")

        # Main container
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left side: faction panel + grid/taskbar
        self.left_container = tk.Frame(self.main_container)
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Faction panel (scrollable) initially hidden
        self.faction_panel_visible = False
        self.faction_panel_frame = tk.Frame(self.left_container, width=200, bg="lightgrey")
        self.faction_panel_canvas = tk.Canvas(self.faction_panel_frame, width=200)
        self.faction_panel_scrollbar = tk.Scrollbar(self.faction_panel_frame, orient="vertical",
                                                    command=self.faction_panel_canvas.yview)
        self.faction_panel_inner = tk.Frame(self.faction_panel_canvas)
        self.faction_panel_inner.bind(
            "<Configure>",
            lambda e: self.faction_panel_canvas.configure(scrollregion=self.faction_panel_canvas.bbox("all"))
        )
        self.faction_panel_canvas.create_window((0, 0), window=self.faction_panel_inner, anchor="nw")
        self.faction_panel_canvas.configure(yscrollcommand=self.faction_panel_scrollbar.set)
        self.faction_panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.faction_panel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Grid and taskbar container
        self.grid_taskbar_container = tk.Frame(self.left_container)
        self.grid_taskbar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Main canvas grid
        self.canvas = tk.Canvas(self.grid_taskbar_container, width=self.canvas_width, height=self.canvas_height, bg="green", highlightthickness=0)
        self.canvas.pack(side=tk.TOP)

        # Taskbar under canvas
        self.taskbar_height = int(self.canvas_height * 0.25)
        self.taskbar = tk.Frame(self.grid_taskbar_container, bg="black", width=self.canvas_width, height=self.taskbar_height)
        self.taskbar.pack_propagate(False)
        self.taskbar.pack(side=tk.TOP, fill=tk.X)

        # Population label
        self.population_var = tk.StringVar()
        self.population_label = tk.Label(self.taskbar, textvariable=self.population_var, fg="white", bg="black", font=("Arial", 12))
        self.population_label.pack(side=tk.LEFT, padx=10)

        # 3x3 detail tile panel bottom-left in taskbar
        self.detail_tile_size = self.cell_size
        self.detail_canvas = tk.Canvas(self.taskbar, width=self.detail_tile_size*3, height=self.detail_tile_size*3, bg="darkgreen", highlightthickness=0)
        self.detail_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Max faction size controls
        self.max_faction_size = 150
        self.max_faction_frame = tk.Frame(self.taskbar, bg="black")
        self.max_faction_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(self.max_faction_frame, text="Max Faction Size:", fg="white", bg="black").pack(side=tk.LEFT)
        self.faction_size_var = tk.StringVar(value=str(self.max_faction_size))
        self.faction_size_entry = tk.Entry(self.max_faction_frame, textvariable=self.faction_size_var, width=5)
        self.faction_size_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(self.max_faction_frame, text="Set", command=self.update_max_faction_size).pack(side=tk.LEFT)

        # Spawn human button bottom right in taskbar
        self.spawn_btn = tk.Button(self.taskbar, text="Spawn Human", command=self.spawn_human)
        self.spawn_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Spawn bear button bottom right
        self.spawn_bear_btn = tk.Button(self.taskbar, text="Spawn Bear", command=self.spawn_bear)
        self.spawn_bear_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Tick rate controls
        self.tick_rates = [1, 2, 3, 5]
        self.current_tick_rate = 2
        self.tick_rate_frame = tk.Frame(self.taskbar, bg="black")
        self.tick_rate_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        for tr in self.tick_rates:
            b = tk.Button(self.tick_rate_frame, text=f"{tr} tick/s", command=lambda rate=tr: self.set_tick_rate(rate))
            b.pack(side=tk.LEFT)

        # Right side: notifications panel
        self.right_container = tk.Frame(self.main_container, width=200, bg="black")
        self.right_container.pack(side=tk.RIGHT, fill=tk.Y)

        self.notif_label = tk.Label(self.right_container, text="Notifications", font=("Arial", 14, "bold"), bg="black", fg="white")
        self.notif_label.pack(pady=5)

        self.notif_text_frame = tk.Frame(self.right_container)
        self.notif_text_frame.pack(fill=tk.BOTH, expand=True)

        self.notif_scrollbar = tk.Scrollbar(self.notif_text_frame)
        self.notif_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notif_text = tk.Text(self.notif_text_frame, height=40, width=40, yscrollcommand=self.notif_scrollbar.set,
                                  bg="black", fg="white", state=tk.DISABLED)
        self.notif_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notif_scrollbar.config(command=self.notif_text.yview)

        # Grid lines cache
        self.lines = []
        self.draw_lines()

        # Data structures
        self.mobs = []
        self.mob_rects = {}
        self.faction_colors = {}
        self.faction_base_colors = ['#ff5555', '#5555ff', '#55ffaa', '#ffaa55', '#aa55ff', '#ffaa55', '#aaff55']
        self.factions = {}
        self.claimed_land = {}
        self.dead_tiles_time = {}
        self.mountains = set()
        self.rocks = set()
        self.show_claims = False
        self.claim_overlay_ids = []
        self.ai_update_counter = 0
        self.tile_mobs = {}
        self.king_cache = {}

        self.mountain_ids = []
        self.rock_ids = []
        self.faction_dot_ids = {}
        self.king_marker_ids = {}

        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.bind('1', self.toggle_faction_panel)
        self.bind('2', self.toggle_claims_display)

        self.tick_count = 0

        self.generate_mountains(count=5)
        self.generate_rocks_around_mountains()
        self.draw_static_terrain()

        self.update_population_display()
        self.draw_mobs(initial=True)
        self.tick()

    def update_max_faction_size(self):
        try:
            new_size = int(self.faction_size_var.get())
            if new_size > 0:
                self.max_faction_size = new_size
                self.add_notification(f"Max faction size set to {new_size}")
            else:
                self.add_notification("Invalid faction size!")
        except ValueError:
            self.add_notification("Invalid faction size!")

    def generate_mountains(self, count=5):
        for _ in range(count):
            sx = random.randint(0, self.grid_size - 10)
            sy = random.randint(0, self.grid_size - 10)
            for dx in range(10):
                for dy in range(10):
                    self.claimed_land[(sx+dx, sy+dy)] = "mountain"
                    self.mountains.add((sx+dx, sy+dy))

    def generate_rocks_around_mountains(self):
        for (mx, my) in self.mountains:
            for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                x, y = mx+dx, my+dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    if (x,y) not in self.mountains and self.claimed_land.get((x,y)) is None:
                        self.claimed_land[(x,y)] = "rock"
                        self.rocks.add((x,y))

    def draw_static_terrain(self):
        for (x, y) in self.mountains:
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rid = self.canvas.create_rectangle(x1, y1, x2, y2, fill='dim grey', outline='')
            self.mountain_ids.append(rid)
        for (x, y) in self.rocks:
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rid = self.canvas.create_rectangle(x1, y1, x2, y2, fill='grey', outline='')
            self.rock_ids.append(rid)

    def add_notification(self, msg):
        self.notif_text.configure(state=tk.NORMAL)
        self.notif_text.insert(tk.END, msg + "\n")
        self.notif_text.see(tk.END)
        self.notif_text.configure(state=tk.DISABLED)

    def draw_lines(self):
        if self.lines:
            return
        color = "#005500"
        for i in range(self.grid_size+1):
            x = i*self.cell_size
            y = i*self.cell_size
            self.lines.append(self.canvas.create_line(x, 0, x, self.canvas_height, fill=color))
            self.lines.append(self.canvas.create_line(0, y, self.canvas_width, y, fill=color))

    def on_mouse_move(self, event):
        tile_x = max(0, min(self.grid_size-1, event.x // self.cell_size))
        tile_y = max(0, min(self.grid_size-1, event.y // self.cell_size))
        self.update_detail_grid(tile_x, tile_y)

    def update_detail_grid(self, cx, cy):
        self.detail_canvas.delete("all")
        sx = max(0, cx-1)
        sy = max(0, cy-1)
        for dx in range(3):
            for dy in range(3):
                x, y = sx+dx, sy+dy
                if x >= self.grid_size or y >= self.grid_size:
                    continue
                color = "green"
                c = self.claimed_land.get((x, y))
                if c == "dead_tile":
                    color = "light grey"
                elif c == "mountain":
                    color = "dim grey"
                elif c == "rock":
                    color = "grey"
                mob = next((m for m in self.mobs if m.x==x and m.y==y), None)
                if mob:
                    if mob.mob_type == "Human":
                        if mob.job == "civilian":
                            color = "sienna"
                        elif mob.job == "guard":
                            color = "orange"
                        elif mob.job == "warrior":
                            color = "red"
                        else:
                            color = "brown"
                    elif mob.mob_type == "Bear":
                        color = "black"
                    elif mob.mob_type == "Zombie":
                        color = "purple"
                self.detail_canvas.create_rectangle(
                    dx*self.detail_tile_size, dy*self.detail_tile_size,
                    (dx+1)*self.detail_tile_size, (dy+1)*self.detail_tile_size,
                    fill=color)

    def set_tick_rate(self, rate):
        self.current_tick_rate = rate
        
    def tick(self):
        self.tick_count += 1
        self.ai_update_counter += 1
        
        if self.ai_update_counter >= 5:
            self.ai_update_counter = 0
            self.handle_fertility_updates()
            self.handle_aging_and_death()
            self.handle_dead_tiles_revert()
            self.handle_zombie_reanimation()
            self.handle_reproduction()
            self.handle_fights()
            self.handle_zombie_swarming()
            self.handle_neutral_faction_creation()
            self.promote_guards()
            self.assign_warriors()
            self.clear_attack_alerts()

        self.cache_tile_mobs()
        self.cache_faction_kings()

        self.move_mobs_advanced()
        self.update_population_display()
        self.update_canvas_mobs()

        self.after(1000 // self.current_tick_rate, self.tick)

    def cache_tile_mobs(self):
        self.tile_mobs.clear()
        for mob in self.mobs:
            self.tile_mobs.setdefault((mob.x, mob.y), []).append(mob)

    def cache_faction_kings(self):
        self.king_cache.clear()
        for faction, members in self.factions.items():
            king = next((m for m in members if m.is_king), None)
            if king:
                self.king_cache[faction] = king

    def handle_fertility_updates(self):
        for mob in self.mobs:
            if mob.mob_type != "Human":
                continue
            mob.fertility_ticks += 1
            if mob.fertility_ticks >= 150:  # 15 years in simulation time
                mob.fertility_meter = 100
                mob.fertility_ticks = 0

    def handle_aging_and_death(self):
        dead = []
        for mob in self.mobs:
            if mob.mob_type == "Human":
                mob.age_ticks += 1
                if mob.age_ticks >= 10:
                    mob.age += 1
                    mob.age_ticks = 0
                    if mob.health < 100:
                        mob.health = min(100, mob.health + 1)
                    if 50 <= mob.age <= 80 and mob.health <= 0:
                        dead.append(mob)
            elif mob.mob_type == "Bear":
                # Bears don't age the same way, but can still die from combat
                if mob.health <= 0:
                    dead.append(mob)
            elif mob.mob_type == "Zombie":
                # Zombies don't age or heal
                if mob.health <= 0:
                    dead.append(mob)
        
        for mob in dead:
            if mob.faction in self.factions and mob in self.factions[mob.faction]:
                self.factions[mob.faction].remove(mob)
                if mob.job == "guard":
                    self.add_notification(f"{mob.name} (Guard) died, will promote replacement.")
                if mob.is_king:
                    self.handle_king_death(mob.faction)
                if not self.factions[mob.faction]:
                    self.remove_claimed_land_for_faction(mob.faction)
                    self.add_notification(f"Faction {mob.faction} died out.")
                    del self.factions[mob.faction]
            self.mobs.remove(mob)
            if mob.mob_type == "Human":
                self.claimed_land[(mob.x, mob.y)] = "dead_tile"
                self.dead_tiles_time[(mob.x, mob.y)] = self.tick_count
            self.add_notification(f"{mob.name} died.")

    def handle_dead_tiles_revert(self):
        to_revert = [pos for pos, tick in self.dead_tiles_time.items() if (self.tick_count - tick) >= 100]
        for pos in to_revert:
            del self.dead_tiles_time[pos]
            if self.claimed_land.get(pos) == "dead_tile":
                if pos in self.rocks:
                    self.claimed_land[pos] = "rock"
                else:
                    del self.claimed_land[pos]
                self.add_notification(f"Tile {pos} reverted to natural state.")

    def handle_zombie_reanimation(self):
        dead_positions = list(self.dead_tiles_time.keys())
        for pos in dead_positions:
            if random.randint(1, 100) == 1:  # 1% chance per dead tile per cycle
                x, y = pos
                if not any(m.x == x and m.y == y for m in self.mobs):
                    zombie_name = f"Zombie_{len([m for m in self.mobs if m.mob_type == 'Zombie']) + 1}"
                    zombie = Mob(x, y, name=zombie_name, mob_type="Zombie", faction=None, job="zombie", health=50)
                    self.mobs.append(zombie)
                    self.add_notification(f"{zombie_name} reanimated at ({x}, {y})!")
                    # Remove dead tile since zombie took its place
                    del self.dead_tiles_time[pos]
                    if self.claimed_land.get(pos) == "dead_tile":
                        del self.claimed_land[pos]

    def handle_reproduction(self):
        checked_pairs = set()
        for mob1 in self.mobs:
            if mob1.mob_type != "Human" or mob1.faction is None:
                continue
            if mob1.fertility_meter < 100 or mob1.children_count >= mob1.max_children:
                continue
            
            faction_size = len(self.factions.get(mob1.faction, []))
            if faction_size >= self.max_faction_size:
                continue
                
            for dx in range(-1,2):
                for dy in range(-1,2):
                    x, y = mob1.x + dx, mob1.y + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        for mob2 in self.tile_mobs.get((x,y), []):
                            if mob2 == mob1 or mob2.faction != mob1.faction:
                                continue
                            if mob2.fertility_meter < 100 or mob2.children_count >= mob2.max_children:
                                continue
                            pair = tuple(sorted((mob1.name, mob2.name)))
                            if pair in checked_pairs:
                                continue
                            checked_pairs.add(pair)
                            if random.randint(1,10) == 1:  # Reduced chance since both need 100% fertility
                                self.spawn_child_near(mob1, mob2)

    def spawn_child_near(self, mob1, mob2):
        possible = set()
        for mob in (mob1, mob2):
            for dx in range(-1,2):
                for dy in range(-1,2):
                    x, y = mob.x + dx, mob.y + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        if not any(m.x == x and m.y == y for m in self.mobs) and self.claimed_land.get((x,y)) not in ("dead_tile","mountain","rock"):
                            possible.add((x,y))
        if not possible:
            return
        x,y = random.choice(list(possible))
        child_name = f"{mob1.faction}_child_{len(self.mobs)+1}"
        child = Mob(x, y, name=child_name, mob_type="Human", faction=mob1.faction, parents=[mob1, mob2], job="civilian")
        child.max_children = random.randint(1, 3)
        mob1.children.append(child)
        mob2.children.append(child)
        mob1.children_count += 1
        mob2.children_count += 1
        mob1.fertility_meter = 0
        mob2.fertility_meter = 0
        mob1.fertility_ticks = 0
        mob2.fertility_ticks = 0
        self.mobs.append(child)
        self.factions[mob1.faction].append(child)
        self.add_notification(f"{child.name} born into faction {mob1.faction} as civilian.")

    def handle_zombie_swarming(self):
        zombies = [m for m in self.mobs if m.mob_type == "Zombie"]
        
        # Check for swarms of 10+ zombies in 10x10 grids
        for zombie in zombies:
            nearby_zombies = []
            for other_zombie in zombies:
                if abs(other_zombie.x - zombie.x) <= 5 and abs(other_zombie.y - zombie.y) <= 5:
                    nearby_zombies.append(other_zombie)
            
            if len(nearby_zombies) >= 10:
                # Find nearest king to target
                nearest_king = None
                min_distance = float('inf')
                for faction, king in self.king_cache.items():
                    distance = abs(king.x - zombie.x) + abs(king.y - zombie.y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_king = king
                
                if nearest_king:
                    # Set swarm target for all nearby zombies
                    for swarm_zombie in nearby_zombies:
                        swarm_zombie.target_attack_pos = (nearest_king.x, nearest_king.y)
                    
                    # Check if any zombie touches faction border
                    king_faction = nearest_king.faction
                    territory = self.get_faction_territory(king_faction)
                    border_tiles = self.get_border_tiles(king_faction)
                    
                    for swarm_zombie in nearby_zombies:
                        zombie_pos = (swarm_zombie.x, swarm_zombie.y)
                        for border_pos in border_tiles:
                            if abs(zombie_pos[0] - border_pos[0]) <= 1 and abs(zombie_pos[1] - border_pos[1]) <= 1:
                                self.alert_warriors(king_faction, zombie_pos)
                                self.add_notification(f"Zombie swarm threatens {king_faction}! Warriors alerted!")
                                break

    def handle_fights(self):
        fought_pairs = set()
        for mob1 in self.mobs:
            if mob1.health <= 0:
                continue
            if mob1.mob_type == "Human" and mob1.faction is None:
                continue
            for pos in self.get_adjacent_positions((mob1.x, mob1.y)):
                for mob2 in self.tile_mobs.get(pos, []):
                    if mob2 == mob1 or mob2.health <= 0:
                        continue
                    
                    # Humans fighting other humans of different factions
                    if mob1.mob_type == "Human" and mob2.mob_type == "Human":
                        if mob1.faction == mob2.faction:
                            continue
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)
                    
                    # Bear attacks humans logic
                    elif mob1.mob_type == "Bear" and mob2.mob_type == "Human":
                        if mob2.job in ("guard", "warrior"):
                            pair = tuple(sorted([mob1.name, mob2.name]))
                            if pair in fought_pairs:
                                continue
                            fought_pairs.add(pair)
                            self.resolve_fight(mob1, mob2)
                        elif mob2.job == "civilian" or mob2.faction is None:
                            continue
                    elif mob2.mob_type == "Bear" and mob1.mob_type == "Human":
                        if mob1.job in ("guard", "warrior"):
                            pair = tuple(sorted([mob1.name, mob2.name]))
                            if pair in fought_pairs:
                                continue
                            fought_pairs.add(pair)
                            self.resolve_fight(mob1, mob2)
                        elif mob1.job == "civilian" or mob1.faction is None:
                            continue
                    
                    # Zombie attacks humans
                    elif mob1.mob_type == "Zombie" and mob2.mob_type == "Human":
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)
                    elif mob2.mob_type == "Zombie" and mob1.mob_type == "Human":
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)
                    
                    # Warriors/Guards vs Zombies
                    elif mob1.mob_type == "Human" and mob1.job in ("guard", "warrior") and mob2.mob_type == "Zombie":
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)

    def resolve_fight(self, mob1, mob2):
        strength_map = {
            "civilian": 1,
            "guard": 4,
            "warrior": 3,
            "bear": 5,
            "zombie": 2
        }
        s1 = strength_map.get(mob1.job, 1) * mob1.health
        s2 = strength_map.get(mob2.job, 1) * mob2.health
        if s1 == s2:
            winner, loser = (mob1, mob2) if random.choice([True, False]) else (mob2, mob1)
        elif s1 > s2:
            winner, loser = mob1, mob2
        else:
            winner, loser = mob2, mob1
        damage = max(10, winner.health // 2)
        loser.health -= damage
        if loser.health < 0:
            loser.health = 0
            winner.kills += 1
            if loser.mob_type == "Human" and loser.job == "civilian" and loser.faction:
                self.alert_warriors(loser.faction, (loser.x, loser.y))
        self.add_notification(f"Fight: {winner.name} ({winner.job}) won vs {loser.name} ({loser.job}), dealt {damage} damage.")

    def alert_warriors(self, faction, pos):
        for mob in self.factions.get(faction, []):
            if mob.job == "warrior":
                mob.alerted = True
                mob.target_attack_pos = pos

    def clear_attack_alerts(self):
        for mob in self.mobs:
            if mob.mob_type == "Human":
                mob.alerted = False
                mob.target_attack_pos = None

    def handle_neutral_faction_creation(self):
        for mob in list(self.mobs):
            if mob.mob_type != "Human" or mob.faction is not None:
                continue
            mob.neutral_ticks += 1
            if mob.neutral_ticks >= 50:
                nearby = [other for other in self.mobs if other.mob_type == "Human" and other.faction is None and abs(other.x - mob.x) <= 5 and abs(other.y - mob.y) <= 5]
                if nearby:
                    faction_name = f"Faction_{mob.name}"
                    for h in nearby:
                        h.faction = faction_name
                        h.neutral_ticks = 0
                        h.job = "civilian"
                    self.factions[faction_name] = nearby
                    for dx in range(-5,6):
                        for dy in range(-5,6):
                            x,y = mob.x+dx, mob.y+dy
                            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                                if self.claimed_land.get((x,y)) not in ("mountain","rock"):
                                    self.claimed_land[(x,y)] = faction_name
                    self.add_notification(f"{mob.name} started new faction {faction_name}.")
                    self.assign_king(faction_name)
                    self.update_faction_colors()

    def assign_king(self, faction_name):
        members = self.factions.get(faction_name, [])
        if not members:
            return
        king = max(members, key=lambda m: m.age)
        king.is_king = True
        king.health = min(king.health*2, 100)
        self.add_notification(f"{king.name} is the king of {faction_name}.")

    def promote_guards(self):
        for faction, members in self.factions.items():
            guards = [m for m in members if m.job == "guard"]
            civilians = [m for m in members if m.job == "civilian" and m.health > 50]
            needed = 10 - len(guards)
            if needed > 0 and civilians:
                civilians.sort(key=lambda m: m.health, reverse=True)
                for civ in civilians[:needed]:
                    civ.job = "guard"
                    civ.health = min(civ.health + 30, 100)
                    self.add_notification(f"{civ.name} promoted to guard in {faction}.")
            guards.sort(key=lambda m: m.health)
            if len(guards) > 10:
                for g in guards[10:]:
                    g.job = "civilian"
                    self.add_notification(f"{g.name} demoted to civilian in {faction}.")

    def assign_warriors(self):
        for faction, members in self.factions.items():
            warriors = [m for m in members if m.job == "warrior"]
            civilians = [m for m in members if m.job == "civilian"]
            total = len(members)
            max_warriors = max(total // 2, 0)
            needed = max_warriors - len(warriors)
            if needed > 0 and civilians:
                civilians.sort(key=lambda m: (m.kills, m.health), reverse=True)
                for civ in civilians[:needed]:
                    civ.job = "warrior"
                    civ.health = min(civ.health + 10, 100)
                    self.add_notification(f"{civ.name} assigned as warrior in {faction}.")
            if len(warriors) > max_warriors:
                for w in warriors[max_warriors:]:
                    w.job = "civilian"
                    self.add_notification(f"{w.name} demoted to civilian in {faction}.")

    def move_mobs_advanced(self):
        for mob in self.mobs:
            if mob.health <= 0:
                continue
            if mob.mob_type == "Bear":
                self.move_bear_ai(mob)
            elif mob.mob_type == "Human":
                if mob.job == "civilian":
                    self.move_civilian_ai(mob)
                elif mob.job == "guard":
                    self.move_guard_ai(mob)
                elif mob.job == "warrior":
                    self.move_warrior_ai(mob)
            elif mob.mob_type == "Zombie":
                self.move_zombie_ai(mob)

    def move_civilian_ai(self, mob):
        # Civilians run from zombies
        nearby_zombies = [m for m in self.mobs if m.mob_type == "Zombie" and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3]
        if nearby_zombies:
            closest_zombie = min(nearby_zombies, key=lambda z: abs(z.x - mob.x) + abs(z.y - mob.y))
            self.move_away_from(mob, (closest_zombie.x, closest_zombie.y))
            return

        if mob.faction is None:
            self.random_move(mob)
            claim = self.claimed_land.get((mob.x, mob.y))
            if claim and claim not in ("mountain", "rock", "dead_tile"):
                mob.faction = claim
                self.factions.setdefault(claim,[]).append(mob)
                self.add_notification(f"{mob.name} joined faction {claim} as civilian.")
        else:
            territory = self.get_faction_territory(mob.faction)
            moves = self.get_valid_moves(mob, [(0,1),(0,-1),(1,0),(-1,0)])
            moves = [d for d in moves if (mob.x+d[0], mob.y+d[1]) in territory]
            if moves:
                dx, dy = random.choice(moves)
                mob.x += dx
                mob.y += dy
            if random.random() < 0.01:
                self.try_claim_land(mob)

    def move_guard_ai(self, mob):
        # Guards run from zombies unless protecting king
        nearby_zombies = [m for m in self.mobs if m.mob_type == "Zombie" and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3]
        king = self.king_cache.get(mob.faction)
        
        if nearby_zombies and king:
            king_distance = abs(mob.x - king.x) + abs(mob.y - king.y)
            if king_distance > 2:  # If not close to king, run from zombies
                closest_zombie = min(nearby_zombies, key=lambda z: abs(z.x - mob.x) + abs(z.y - mob.y))
                self.move_away_from(mob, (closest_zombie.x, closest_zombie.y))
                return

        if king is None or king == mob:
            self.move_civilian_ai(mob)
            return
        dist = abs(mob.x - king.x) + abs(mob.y - king.y)
        if dist > 3:
            self.move_towards(mob, (king.x, king.y))
        else:
            moves = self.get_valid_moves(mob, [(0,1),(0,-1),(1,0),(-1,0)])
            moves = [d for d in moves if abs(mob.x + d[0] - king.x)+abs(mob.y + d[1] - king.y) <= 3]
            if moves:
                dx, dy = random.choice(moves)
                mob.x += dx
                mob.y += dy

    def move_warrior_ai(self, mob):
        # Warriors actively hunt zombies and enemies
        territory = self.get_faction_territory(mob.faction)
        border_tiles = self.get_border_tiles(mob.faction)
        x, y = mob.x, mob.y

        if mob.alerted and mob.target_attack_pos:
            self.move_towards(mob, mob.target_attack_pos, avoid_warriors=True)
            if abs(mob.x - mob.target_attack_pos[0]) <= 1 and abs(mob.y - mob.target_attack_pos[1]) <= 1:
                mob.alerted = False
                mob.target_attack_pos = None
            return

        # Prioritize zombies over other enemies
        zombies = self.scan_for_zombies(mob, 5)
        if zombies:
            nearest_zombie = min(zombies, key=lambda m: abs(m.x - x) + abs(m.y - y))
            self.move_towards(mob, (nearest_zombie.x, nearest_zombie.y), avoid_warriors=True)
            return

        enemies = self.scan_for_enemies(mob, 3)
        if enemies:
            nearest_enemy = min(enemies, key=lambda m: abs(m.x - x) + abs(m.y - y))
            self.move_towards(mob, (nearest_enemy.x, nearest_enemy.y), avoid_warriors=True)
            return

        if (x,y) not in border_tiles:
            if border_tiles:
                closest_border = min(border_tiles, key=lambda p: abs(p[0]-x) + abs(p[1]-y))
                self.move_towards(mob, closest_border, avoid_warriors=True)
            else:
                self.move_civilian_ai(mob)
            return

        nbr_moves = [(0,1),(0,-1),(1,0),(-1,0)]
        border_adjacent = []
        for dx, dy in nbr_moves:
            nx, ny = x+dx, y+dy
            if (nx, ny) in border_tiles:
                blocked = False
                for m in self.tile_mobs.get((nx, ny), []):
                    if m != mob and m.faction == mob.faction and m.job == "warrior":
                        blocked = True
                        break
                if not blocked:
                    border_adjacent.append((nx, ny))
        if border_adjacent:
            nx, ny = random.choice(border_adjacent)
            mob.x, mob.y = nx, ny
        else:
            moves = self.get_valid_moves(mob, nbr_moves)
            moves = [d for d in moves if (mob.x + d[0], mob.y + d[1]) in territory]
            if moves:
                dx, dy = random.choice(moves)
                mob.x += dx
                mob.y += dy

    def move_zombie_ai(self, mob):
        # If zombie has a target from swarming, move towards it
        if hasattr(mob, 'target_attack_pos') and mob.target_attack_pos:
            self.move_towards(mob, mob.target_attack_pos)
            return

        # Look for nearby humans to chase
        nearby_humans = [m for m in self.mobs if m.mob_type == "Human" and abs(m.x - mob.x) <= 5 and abs(m.y - mob.y) <= 5]
        if nearby_humans:
            # Prefer civilians over warriors/guards
            civilians = [h for h in nearby_humans if h.job == "civilian"]
            if civilians:
                target = min(civilians, key=lambda h: abs(h.x - mob.x) + abs(h.y - mob.y))
            else:
                target = min(nearby_humans, key=lambda h: abs(h.x - mob.x) + abs(h.y - mob.y))
            self.move_towards(mob, (target.x, target.y))
            return

        # Look for other zombies to group with
        nearby_zombies = [m for m in self.mobs if m.mob_type == "Zombie" and m != mob and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3]
        if nearby_zombies and len(nearby_zombies) < 5:  # Don't overcrowd
            closest_zombie = min(nearby_zombies, key=lambda z: abs(z.x - mob.x) + abs(z.y - mob.y))
            self.move_towards(mob, (closest_zombie.x, closest_zombie.y))
            return

        # Random movement
        self.random_move(mob)

    def move_bear_ai(self, mob):
        closest_mountain = None
        min_dist = 9999
        for mx, my in self.mountains:
            dist = abs(mx - mob.x) + abs(my - mob.y)
            if dist < min_dist:
                min_dist = dist
                closest_mountain = (mx, my)

        if closest_mountain and min_dist > 5:
            self.move_towards(mob, closest_mountain)
            return

        enemies = self.scan_for_humans_3x3(mob)

        if not enemies:
            self.random_move_near(mob, closest_mountain)
            return

        for h in enemies:
            if h.job in ("guard","warrior"):
                self.move_towards(mob, (h.x, h.y))
                return

        closest_h = min(enemies, key=lambda m: abs(m.x - mob.x) + abs(m.y - mob.y))
        dx = mob.x - closest_h.x
        dy = mob.y - closest_h.y
        move_options = self.get_valid_moves(mob, [(0,1),(0,-1),(1,0),(-1,0)])
        if not move_options:
            return
        def dist_if_move(d):
            nx, ny = mob.x + d[0], mob.y + d[1]
            return abs(nx - closest_h.x) + abs(ny - closest_h.y)
        move_options.sort(key=dist_if_move, reverse=True)
        mob.x += move_options[0][0]
        mob.y += move_options[0][1]

    def scan_for_enemies(self, mob, radius):
        enemies = []
        for other in self.mobs:
            if other == mob or other.health <= 0:
                continue
            if abs(other.x - mob.x) <= radius and abs(other.y - mob.y) <= radius:
                if mob.mob_type == "Human" and other.mob_type == "Human":
                    if mob.faction != other.faction:
                        enemies.append(other)
                elif mob.mob_type == "Human" and other.mob_type == "Bear":
                    enemies.append(other)
                elif mob.mob_type == "Bear" and other.mob_type == "Human":
                    enemies.append(other)
        return enemies

    def scan_for_zombies(self, mob, radius):
        return [m for m in self.mobs if m.mob_type == "Zombie" and abs(m.x - mob.x) <= radius and abs(m.y - mob.y) <= radius and m.health > 0]

    def scan_for_humans_3x3(self, mob):
        return [m for m in self.mobs if m.mob_type == "Human" and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3 and m.health > 0]

    def get_faction_territory(self, faction):
        return set(pos for pos, f in self.claimed_land.items() if f == faction)

    def get_border_tiles(self, faction):
        territory = self.get_faction_territory(faction)
        border_tiles = set()
        for x, y in territory:
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if (nx, ny) not in territory:
                    border_tiles.add((x,y))
                    break
        return border_tiles

    def move_towards(self, mob, target, avoid_warriors=False):
        tx, ty = target
        cx, cy = mob.x, mob.y
        options = []
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        for dx,dy in directions:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.claimed_land.get((nx, ny)) in ("mountain","rock"):
                    continue
                occupied_by = next((m for m in self.mobs if m.x == nx and m.y == ny and m != mob), None)
                if occupied_by:
                    if avoid_warriors and occupied_by.job == "warrior" and occupied_by.faction == mob.faction:
                        continue
                    else:
                        continue
                dist_before = abs(cx - tx) + abs(cy - ty)
                dist_after = abs(nx - tx) + abs(ny - ty)
                if dist_after < dist_before:
                    options.append((nx, ny))
        if options:
            nx, ny = random.choice(options)
            mob.x, mob.y = nx, ny
        else:
            if mob.mob_type == "Human" and mob.faction:
                territory = self.get_faction_territory(mob.faction)
                valid_moves = self.get_valid_moves(mob, directions)
                valid_moves = [d for d in valid_moves if (mob.x + d[0], mob.y + d[1]) in territory]
                if valid_moves:
                    dx, dy = random.choice(valid_moves)
                    mob.x += dx
                    mob.y += dy
            else:
                self.random_move(mob)

    def move_away_from(self, mob, threat_pos):
        tx, ty = threat_pos
        cx, cy = mob.x, mob.y
        options = []
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        for dx,dy in directions:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.claimed_land.get((nx, ny)) in ("mountain","rock"):
                    continue
                occupied_by = next((m for m in self.mobs if m.x == nx and m.y == ny and m != mob), None)
                if occupied_by:
                    continue
                dist_before = abs(cx - tx) + abs(cy - ty)
                dist_after = abs(nx - tx) + abs(ny - ty)
                if dist_after > dist_before:  # Moving away increases distance
                    options.append((nx, ny))
        if options:
            nx, ny = random.choice(options)
            mob.x, mob.y = nx, ny
        else:
            self.random_move(mob)

    def random_move(self, mob):
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        moves = self.get_valid_moves(mob, directions)
        if moves:
            dx, dy = random.choice(moves)
            mob.x += dx
            mob.y += dy

    def random_move_near(self, mob, point):
        if point is None:
            self.random_move(mob)
            return
        px, py = point
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        moves = self.get_valid_moves(mob, directions)
        moves = [d for d in moves if abs(mob.x + d[0] - px) <= 10 and abs(mob.y + d[1] - py) <= 10]
        if moves:
            dx, dy = random.choice(moves)
            mob.x += dx
            mob.y += dy
        else:
            self.random_move(mob)

    def get_valid_moves(self, mob, directions):
        valid = []
        for dx, dy in directions:
            nx, ny = mob.x + dx, mob.y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.claimed_land.get((nx, ny)) in ("mountain", "rock"):
                    continue
                if any(m.x == nx and m.y == ny for m in self.mobs if m != mob):
                    continue
                valid.append((dx, dy))
        return valid

    def try_claim_land(self, mob):
        if mob.faction is None:
            return
        if mob.job not in ("civilian", "guard"):
            return
        adjacent = [(mob.x+dx, mob.y+dy) for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]]
        claimed = False
        for x, y in adjacent:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                current_claim = self.claimed_land.get((x,y))
                if current_claim is None or current_claim == "dead_tile":
                    if (x,y) not in self.mountains and (x,y) not in self.rocks:
                        if random.random() < 0.02:
                            self.claimed_land[(x,y)] = mob.faction
                            claimed = True
                            self.add_notification(f"{mob.name} ({mob.job}) expanded territory at ({x},{y}).")
        if claimed and self.show_claims:
            self.draw_claims_overlay()

    def spawn_human(self):
        empty_tiles = [(x,y) for x in range(self.grid_size) for y in range(self.grid_size)
                       if (not any(m.x==x and m.y==y for m in self.mobs) and self.claimed_land.get((x,y)) not in ("dead_tile","mountain","rock"))]
        if not empty_tiles:
            return
        x,y = random.choice(empty_tiles)
        name = f"Human{len(self.mobs)+1}"
        human = Mob(x,y,name=name,mob_type="Human",faction=None, job="civilian")
        human.max_children = random.randint(1, 3)
        self.mobs.append(human)
        self.add_notification(f"{name} spawned at ({x},{y}) as civilian.")

    def spawn_bear(self):
        if not self.mountains:
            self.add_notification("No mountains to spawn bears near.")
            return
        mx, my = random.choice(list(self.mountains))
        for _ in range(100):
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            x, y = mx+dx, my+dy
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                if self.claimed_land.get((x,y)) in ("mountain","rock"):
                    continue
                if any(m.x == x and m.y == y for m in self.mobs):
                    continue
                name = f"Bear{len([m for m in self.mobs if m.mob_type == 'Bear'])+1}"
                bear = Mob(x,y,name=name,mob_type="Bear", faction=None, job="bear", health=100)
                self.mobs.append(bear)
                self.add_notification(f"{name} spawned near mountain at ({x},{y}).")
                return
        self.add_notification("Failed to spawn bear near mountain.")

    def update_population_display(self):
        humans = [m for m in self.mobs if m.mob_type == "Human"]
        zombies = [m for m in self.mobs if m.mob_type == "Zombie"]
        bears = [m for m in self.mobs if m.mob_type == "Bear"]
        self.population_var.set(f"Humans: {len(humans)} | Zombies: {len(zombies)} | Bears: {len(bears)}")

    def update_canvas_mobs(self):
        for mob in list(self.mob_rects.keys()):
            if mob not in self.mobs:
                self.canvas.delete(self.mob_rects[mob])
                del self.mob_rects[mob]
                if mob in self.faction_dot_ids:
                    self.canvas.delete(self.faction_dot_ids[mob])
                    del self.faction_dot_ids[mob]
                if mob in self.king_marker_ids:
                    self.canvas.delete(self.king_marker_ids[mob])
                    del self.king_marker_ids[mob]

        for mob in self.mobs:
            px1 = mob.x * self.cell_size + 1
            py1 = mob.y * self.cell_size + 1
            px2 = (mob.x + 1) * self.cell_size - 1
            py2 = (mob.y + 1) * self.cell_size - 1

            if mob not in self.mob_rects:
                color = "brown"
                if mob.mob_type == "Bear":
                    color = "black"
                elif mob.mob_type == "Zombie":
                    color = "purple"
                else:
                    if mob.job == "civilian":
                        color = "sienna"
                    elif mob.job == "guard":
                        color = "orange"
                    elif mob.job == "warrior":
                        color = "red"
                rect_id = self.canvas.create_rectangle(px1, py1, px2, py2, fill=color, outline="")
                self.mob_rects[mob] = rect_id
            else:
                rect_id = self.mob_rects[mob]
                coords = self.canvas.coords(rect_id)
                desired = [px1, py1, px2, py2]
                if coords != desired:
                    self.canvas.coords(rect_id, *desired)

            if mob.mob_type == "Human" and mob.faction:
                ccolor = self.faction_colors.get(mob.faction, "white")
                cx = mob.x * self.cell_size + self.cell_size // 2
                cy = mob.y * self.cell_size + self.cell_size // 2
                if mob not in self.faction_dot_ids:
                    dot_id = self.canvas.create_oval(cx, cy, cx+2, cy+2, fill=ccolor, outline=ccolor)
                    self.faction_dot_ids[mob] = dot_id
                else:
                    self.canvas.coords(self.faction_dot_ids[mob], cx, cy, cx+2, cy+2)
                    self.canvas.itemconfig(self.faction_dot_ids[mob], fill=ccolor, outline=ccolor)
            else:
                if mob in self.faction_dot_ids:
                    self.canvas.delete(self.faction_dot_ids[mob])
                    del self.faction_dot_ids[mob]

            if mob.is_king:
                rid = self.mob_rects[mob]
                coords = self.canvas.coords(rid)
                x1, y1, x2, y2 = coords
                if mob not in self.king_marker_ids:
                    marker_id = self.canvas.create_rectangle(x1, y1, (x1 + x2) / 2, y2, fill='yellow', stipple='gray25', outline='')
                    self.king_marker_ids[mob] = marker_id
                else:
                    self.canvas.coords(self.king_marker_ids[mob], x1, y1, (x1 + x2) / 2, y2)
                    self.canvas.itemconfig(self.king_marker_ids[mob], state='normal')
            else:
                if mob in self.king_marker_ids:
                    self.canvas.itemconfig(self.king_marker_ids[mob], state='hidden')

        if self.show_claims:
            self.draw_claims_overlay()
        else:
            self.clear_claims_overlay()

    def draw_mobs(self, initial=False):
        if initial:
            for mob in self.mobs:
                px1 = mob.x * self.cell_size + 1
                py1 = mob.y * self.cell_size + 1
                px2 = (mob.x+1) * self.cell_size - 1
                py2 = (mob.y+1) * self.cell_size - 1

                color = "brown"
                if mob.mob_type == "Bear":
                    color = "black"
                elif mob.mob_type == "Zombie":
                    color = "purple"
                else:
                    if mob.job == "civilian":
                        color = "sienna"
                    elif mob.job == "guard":
                        color = "orange"
                    elif mob.job == "warrior":
                        color = "red"

                rect_id = self.canvas.create_rectangle(px1, py1, px2, py2, fill=color, outline="")
                self.mob_rects[mob] = rect_id

                if mob.mob_type == "Human" and mob.faction:
                    ccolor = self.faction_colors.get(mob.faction, "white")
                    cx = mob.x * self.cell_size + self.cell_size // 2
                    cy = mob.y * self.cell_size + self.cell_size // 2
                    dot_id = self.canvas.create_oval(cx, cy, cx+2, cy+2, fill=ccolor, outline=ccolor)
                    self.faction_dot_ids[mob] = dot_id

                if mob.is_king:
                    marker_id = self.canvas.create_rectangle(px1, py1, (px1+px2)/2, py2, fill='yellow', stipple='gray25', outline='')
                    self.king_marker_ids[mob] = marker_id

            if self.show_claims:
                self.draw_claims_overlay()

    def draw_claims_overlay(self):
        self.clear_claims_overlay()
        self.update_faction_colors()
        for (x, y), faction in self.claimed_land.items():
            if faction == "dead_tile":
                color = "#bbbbbb"
            elif faction == "mountain" or faction == "rock":
                continue
            else:
                color = self.faction_colors.get(faction, "#000000")
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rid = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", stipple="gray25")
            self.claim_overlay_ids.append(rid)

    def clear_claims_overlay(self):
        for rid in self.claim_overlay_ids:
            self.canvas.delete(rid)
        self.claim_overlay_ids.clear()

    def update_faction_colors(self):
        factions = sorted(self.factions.keys())
        for i, fn in enumerate(factions):
            if fn not in self.faction_colors:
                self.faction_colors[fn] = self.faction_base_colors[i % len(self.faction_base_colors)]

    def toggle_claims_display(self, event=None):
        self.show_claims = not self.show_claims
        if self.show_claims:
            self.add_notification("Showing faction land claims.")
            self.draw_claims_overlay()
        else:
            self.add_notification("Hiding faction land claims.")
            self.clear_claims_overlay()

    def on_mouse_click(self, event):
        clicked = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked:
            mob = None
            for m, cid in self.mob_rects.items():
                if cid == item:
                    mob = m
                    break
            if mob:
                self.show_mob_panel(mob)
                break

    def show_mob_panel(self, mob):
        win = tk.Toplevel(self)
        win.title(f"{mob.name} info")
        faction = mob.faction or "Neutral"
        job = getattr(mob, 'job', 'unknown')
        txt = (f"Name: {mob.name}\nType: {mob.mob_type}\nJob: {job}\nFaction: {faction}"
               f"\nAge: {mob.age} years\nHealth: {mob.health}\nKills: {mob.kills}")
        
        if mob.mob_type == "Human":
            txt += f"\nFertility: {mob.fertility_meter}%"
            txt += f"\nChildren: {mob.children_count}/{mob.max_children}"
        
        if mob.parents:
            txt += "\nParents: " + ", ".join(p.name for p in mob.parents)
        else:
            txt += "\nParents: Unknown"
        if mob.children:
            txt += "\nChildren: " + ", ".join(c.name for c in mob.children)
        else:
            txt += "\nChildren: None"
        if mob.is_king:
            txt += "\nStatus: King"
        label = tk.Label(win, text=txt, font=("Arial", 12), justify=tk.LEFT)
        label.pack(padx=10, pady=10)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=5)

import tkinter as tk
import random


class Mob:
    def __init__(self, x, y, name, mob_type, faction=None, parents=None, health=100, job="civilian"):
        self.x = x
        self.y = y
        self.name = name
        self.mob_type = mob_type  # "Human", "Bear", or "Zombie"
        self.faction = faction
        self.age = 0
        self.age_ticks = 0
        self.neutral_ticks = 0
        self.parents = parents or []
        self.children = []
        self.health = health
        self.is_king = False
        self.job = job  # "civilian", "guard", "warrior", "bear", or "zombie"
        self.kills = 0
        self.under_attack = False
        self.alerted = False  # Warriors alerted to assist
        self.target_attack_pos = None
        self.fertility_meter = 0
        self.fertility_ticks = 0
        self.children_count = 0
        self.max_children = random.randint(1, 3)


class GreenGridGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Green Grid Faction Simulation")


        self.grid_size = 100
        self.cell_size = 5
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size


        window_width = self.canvas_width + 400
        window_height = self.canvas_height + int(self.canvas_height * 0.25)
        self.geometry(f"{window_width}x{window_height}")


        # Basic setup
        self.grid_size = 100
        self.cell_size = 5
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        window_width = self.canvas_width + 400  # for side panels
        window_height = self.canvas_height + int(self.canvas_height * 0.25)
        self.geometry(f"{window_width}x{window_height}")


        # Main container
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)


        # Left side: faction panel + grid/taskbar
        self.left_container = tk.Frame(self.main_container)
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # Faction panel (scrollable) initially hidden
        self.faction_panel_visible = False
        self.faction_panel_frame = tk.Frame(self.left_container, width=200, bg="lightgrey")
        self.faction_panel_canvas = tk.Canvas(self.faction_panel_frame, width=200)
        self.faction_panel_scrollbar = tk.Scrollbar(self.faction_panel_frame, orient="vertical",
                                                    command=self.faction_panel_canvas.yview)
        self.faction_panel_inner = tk.Frame(self.faction_panel_canvas)
        self.faction_panel_inner.bind(
            "<Configure>",
            lambda e: self.faction_panel_canvas.configure(scrollregion=self.faction_panel_canvas.bbox("all"))
        )
        self.faction_panel_canvas.create_window((0, 0), window=self.faction_panel_inner, anchor="nw")
        self.faction_panel_canvas.configure(yscrollcommand=self.faction_panel_scrollbar.set)
        self.faction_panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.faction_panel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        # Grid and taskbar container
        self.grid_taskbar_container = tk.Frame(self.left_container)
        self.grid_taskbar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Main canvas grid
        self.canvas = tk.Canvas(self.grid_taskbar_container, width=self.canvas_width, height=self.canvas_height, bg="green", highlightthickness=0)
        self.canvas.pack(side=tk.TOP)


        # Taskbar under canvas
        self.taskbar_height = int(self.canvas_height * 0.25)
        self.taskbar = tk.Frame(self.grid_taskbar_container, bg="black", width=self.canvas_width, height=self.taskbar_height)
        self.taskbar.pack_propagate(False)
        self.taskbar.pack(side=tk.TOP, fill=tk.X)


        # Population label
        self.population_var = tk.StringVar()
        self.population_label = tk.Label(self.taskbar, textvariable=self.population_var, fg="white", bg="black", font=("Arial", 12))
        self.population_label.pack(side=tk.LEFT, padx=10)


        # 3x3 detail tile panel bottom-left in taskbar
        self.detail_tile_size = self.cell_size
        self.detail_canvas = tk.Canvas(self.taskbar, width=self.detail_tile_size*3, height=self.detail_tile_size*3, bg="darkgreen", highlightthickness=0)
        self.detail_canvas.pack(side=tk.LEFT, padx=10, pady=10)


        # Max faction size controls
        self.max_faction_size = 150
        self.max_faction_frame = tk.Frame(self.taskbar, bg="black")
        self.max_faction_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(self.max_faction_frame, text="Max Faction Size:", fg="white", bg="black").pack(side=tk.LEFT)
        self.faction_size_var = tk.StringVar(value=str(self.max_faction_size))
        self.faction_size_entry = tk.Entry(self.max_faction_frame, textvariable=self.faction_size_var, width=5)
        self.faction_size_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(self.max_faction_frame, text="Set", command=self.update_max_faction_size).pack(side=tk.LEFT)


        # Spawn human button bottom right in taskbar
        self.spawn_btn = tk.Button(self.taskbar, text="Spawn Human", command=self.spawn_human)
        self.spawn_btn.pack(side=tk.RIGHT, padx=10, pady=10)


        # Spawn bear button bottom right
        self.spawn_bear_btn = tk.Button(self.taskbar, text="Spawn Bear", command=self.spawn_bear)
        self.spawn_bear_btn.pack(side=tk.RIGHT, padx=10, pady=10)


        # Tick rate controls
        self.tick_rates = [1, 2, 3, 5]
        self.current_tick_rate = 2
        self.tick_rate_frame = tk.Frame(self.taskbar, bg="black")
        self.tick_rate_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        for tr in self.tick_rates:
            b = tk.Button(self.tick_rate_frame, text=f"{tr} tick/s", command=lambda rate=tr: self.set_tick_rate(rate))
            b.pack(side=tk.LEFT)


        # Right side: notifications panel
        self.right_container = tk.Frame(self.main_container, width=200, bg="black")
        self.right_container.pack(side=tk.RIGHT, fill=tk.Y)


        self.notif_label = tk.Label(self.right_container, text="Notifications", font=("Arial", 14, "bold"), bg="black", fg="white")
        self.notif_label.pack(pady=5)


        self.notif_text_frame = tk.Frame(self.right_container)
        self.notif_text_frame.pack(fill=tk.BOTH, expand=True)


        self.notif_scrollbar = tk.Scrollbar(self.notif_text_frame)
        self.notif_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        self.notif_text = tk.Text(self.notif_text_frame, height=40, width=40, yscrollcommand=self.notif_scrollbar.set,
                                  bg="black", fg="white", state=tk.DISABLED)
        self.notif_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notif_scrollbar.config(command=self.notif_text.yview)


        # Grid lines cache
        self.lines = []
        self.draw_lines()


        # Data structures
        self.mobs = []
        self.mob_rects = {}
        self.faction_colors = {}
        self.faction_base_colors = ['#ff5555', '#5555ff', '#55ffaa', '#ffaa55', '#aa55ff', '#ffaa55', '#aaff55']
        self.factions = {}
        self.claimed_land = {}
        self.dead_tiles_time = {}
        self.mountains = set()
        self.rocks = set()
        self.show_claims = False
        self.claim_overlay_ids = []
        self.ai_update_counter = 0
        self.tile_mobs = {}
        self.king_cache = {}


        self.mountain_ids = []
        self.rock_ids = []
        self.faction_dot_ids = {}
        self.king_marker_ids = {}


        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.bind('1', self.toggle_faction_panel)
        self.bind('2', self.toggle_claims_display)


        self.tick_count = 0


        self.generate_mountains(count=5)
        self.generate_rocks_around_mountains()
        self.draw_static_terrain()


        self.update_population_display()
        self.draw_mobs(initial=True)
        self.tick()


    def update_max_faction_size(self):
        try:
            new_size = int(self.faction_size_var.get())
            if new_size > 0:
                self.max_faction_size = new_size
                self.add_notification(f"Max faction size set to {new_size}")
            else:
                self.add_notification("Invalid faction size!")
        except ValueError:
            self.add_notification("Invalid faction size!")


    def generate_mountains(self, count=5):
        for _ in range(count):
            sx = random.randint(0, self.grid_size - 10)
            sy = random.randint(0, self.grid_size - 10)
            for dx in range(10):
                for dy in range(10):
                    self.claimed_land[(sx+dx, sy+dy)] = "mountain"
                    self.mountains.add((sx+dx, sy+dy))


    def generate_rocks_around_mountains(self):
        for (mx, my) in self.mountains:
            for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                x, y = mx+dx, my+dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    if (x,y) not in self.mountains and self.claimed_land.get((x,y)) is None:
                        self.claimed_land[(x,y)] = "rock"
                        self.rocks.add((x,y))


    def draw_static_terrain(self):
        for (x, y) in self.mountains:
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rid = self.canvas.create_rectangle(x1, y1, x2, y2, fill='dim grey', outline='')
            self.mountain_ids.append(rid)
        for (x, y) in self.rocks:
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rid = self.canvas.create_rectangle(x1, y1, x2, y2, fill='grey', outline='')
            self.rock_ids.append(rid)


    def add_notification(self, msg):
        self.notif_text.configure(state=tk.NORMAL)
        self.notif_text.insert(tk.END, msg + "\n")
        self.notif_text.see(tk.END)
        self.notif_text.configure(state=tk.DISABLED)


    def draw_lines(self):
        if self.lines:
            return
        color = "#005500"
        for i in range(self.grid_size+1):
            x = i*self.cell_size
            y = i*self.cell_size
            self.lines.append(self.canvas.create_line(x, 0, x, self.canvas_height, fill=color))
            self.lines.append(self.canvas.create_line(0, y, self.canvas_width, y, fill=color))


    def on_mouse_move(self, event):
        tile_x = max(0, min(self.grid_size-1, event.x // self.cell_size))
        tile_y = max(0, min(self.grid_size-1, event.y // self.cell_size))
        self.update_detail_grid(tile_x, tile_y)


    def update_detail_grid(self, cx, cy):
        self.detail_canvas.delete("all")
        sx = max(0, cx-1)
        sy = max(0, cy-1)
        for dx in range(3):
            for dy in range(3):
                x, y = sx+dx, sy+dy
                if x >= self.grid_size or y >= self.grid_size:
                    continue
                color = "green"
                c = self.claimed_land.get((x, y))
                if c == "dead_tile":
                    color = "light grey"
                elif c == "mountain":
                    color = "dim grey"
                elif c == "rock":
                    color = "grey"
                mob = next((m for m in self.mobs if m.x==x and m.y==y), None)
                if mob:
                    if mob.mob_type == "Human":
                        if mob.job == "civilian":
                            color = "sienna"
                        elif mob.job == "guard":
                            color = "orange"
                        elif mob.job == "warrior":
                            color = "red"
                        else:
                            color = "brown"
                    elif mob.mob_type == "Bear":
                        color = "black"
                    elif mob.mob_type == "Zombie":
                        color = "purple"
                self.detail_canvas.create_rectangle(
                    dx*self.detail_tile_size, dy*self.detail_tile_size,
                    (dx+1)*self.detail_tile_size, (dy+1)*self.detail_tile_size,
                    fill=color)


    def set_tick_rate(self, rate):
        self.current_tick_rate = rate
        
    def tick(self):
        self.tick_count += 1
        self.ai_update_counter += 1
        
        if self.ai_update_counter >= 5:
            self.ai_update_counter = 0
            self.handle_fertility_updates()
            self.handle_aging_and_death()
            self.handle_dead_tiles_revert()
            self.handle_zombie_reanimation()
            self.handle_reproduction()
            self.handle_fights()
            self.handle_zombie_swarming()
            self.handle_neutral_faction_creation()
            self.promote_guards()
            self.assign_warriors()
            self.clear_attack_alerts()


        self.cache_tile_mobs()
        self.cache_faction_kings()


        self.move_mobs_advanced()
        self.update_population_display()
        self.update_canvas_mobs()


        self.after(1000 // self.current_tick_rate, self.tick)


    def cache_tile_mobs(self):
        self.tile_mobs.clear()
        for mob in self.mobs:
            self.tile_mobs.setdefault((mob.x, mob.y), []).append(mob)


    def cache_faction_kings(self):
        self.king_cache.clear()
        for faction, members in self.factions.items():
            king = next((m for m in members if m.is_king), None)
            if king:
                self.king_cache[faction] = king



    def handle_fertility_updates(self):
        for mob in self.mobs:
            if mob.mob_type != "Human":
                continue
            mob.fertility_ticks += 1
            if mob.fertility_ticks >= 150:  # 15 years in simulation time
                mob.fertility_meter = 100
                mob.fertility_ticks = 0


    def handle_aging_and_death(self):
        dead = []
        for mob in self.mobs:
            if mob.mob_type == "Human":
                mob.age_ticks += 1
                if mob.age_ticks >= 10:
                    mob.age += 1
                    mob.age_ticks = 0
                    if mob.health < 100:
                        mob.health = min(100, mob.health + 1)
                    if 50 <= mob.age <= 80 and mob.health <= 0:
                        dead.append(mob)
            elif mob.mob_type == "Bear":
                # Bears don't age the same way, but can still die from combat
                if mob.health <= 0:
                    dead.append(mob)
            elif mob.mob_type == "Zombie":
                # Zombies don't age or heal
                if mob.health <= 0:
                    dead.append(mob)
        
        for mob in dead:
            if mob.faction in self.factions and mob in self.factions[mob.faction]:
                self.factions[mob.faction].remove(mob)
                if mob.job == "guard":
                    self.add_notification(f"{mob.name} (Guard) died, will promote replacement.")
                if mob.is_king:
                    self.handle_king_death(mob.faction)
                if not self.factions[mob.faction]:
                    self.remove_claimed_land_for_faction(mob.faction)
                    self.add_notification(f"Faction {mob.faction} died out.")
                    del self.factions[mob.faction]
            self.mobs.remove(mob)
            if mob.mob_type == "Human":
                self.claimed_land[(mob.x, mob.y)] = "dead_tile"
                self.dead_tiles_time[(mob.x, mob.y)] = self.tick_count
            self.add_notification(f"{mob.name} died.")


    def handle_dead_tiles_revert(self):
        to_revert = [pos for pos, tick in self.dead_tiles_time.items() if (self.tick_count - tick) >= 100]
        for pos in to_revert:
            del self.dead_tiles_time[pos]
            if self.claimed_land.get(pos) == "dead_tile":
                if pos in self.rocks:
                    self.claimed_land[pos] = "rock"
                else:
                    del self.claimed_land[pos]
                self.add_notification(f"Tile {pos} reverted to natural state.")


    def handle_zombie_reanimation(self):
        dead_positions = list(self.dead_tiles_time.keys())
        for pos in dead_positions:
            if random.randint(1, 100) == 1:  # 1% chance per dead tile per cycle
                x, y = pos
                if not any(m.x == x and m.y == y for m in self.mobs):
                    zombie_name = f"Zombie_{len([m for m in self.mobs if m.mob_type == 'Zombie']) + 1}"
                    zombie = Mob(x, y, name=zombie_name, mob_type="Zombie", faction=None, job="zombie", health=50)
                    self.mobs.append(zombie)
                    self.add_notification(f"{zombie_name} reanimated at ({x}, {y})!")
                    # Remove dead tile since zombie took its place
                    del self.dead_tiles_time[pos]
                    if self.claimed_land.get(pos) == "dead_tile":
                        del self.claimed_land[pos]


    def handle_reproduction(self):
        checked_pairs = set()
        for mob1 in self.mobs:
            if mob1.mob_type != "Human" or mob1.faction is None:
                continue
            if mob1.fertility_meter < 100 or mob1.children_count >= mob1.max_children:
                continue
            
            faction_size = len(self.factions.get(mob1.faction, []))
            if faction_size >= self.max_faction_size:
                continue
                
            for dx in range(-1,2):
                for dy in range(-1,2):
                    x, y = mob1.x + dx, mob1.y + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        for mob2 in self.tile_mobs.get((x,y), []):
                            if mob2 == mob1 or mob2.faction != mob1.faction:
                                continue
                            if mob2.fertility_meter < 100 or mob2.children_count >= mob2.max_children:
                                continue
                            pair = tuple(sorted((mob1.name, mob2.name)))
                            if pair in checked_pairs:
                                continue
                            checked_pairs.add(pair)
                            if random.randint(1,10) == 1:  # Reduced chance since both need 100% fertility
                                self.spawn_child_near(mob1, mob2)


    def spawn_child_near(self, mob1, mob2):
        possible = set()
        for mob in (mob1, mob2):
            for dx in range(-1,2):
                for dy in range(-1,2):
                    x, y = mob.x + dx, mob.y + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        if not any(m.x == x and m.y == y for m in self.mobs) and self.claimed_land.get((x,y)) not in ("dead_tile","mountain","rock"):
                            possible.add((x,y))
        if not possible:
            return
        x,y = random.choice(list(possible))
        child_name = f"{mob1.faction}_child_{len(self.mobs)+1}"
        child = Mob(x, y, name=child_name, mob_type="Human", faction=mob1.faction, parents=[mob1, mob2], job="civilian")
        child.max_children = random.randint(1, 3)
        mob1.children.append(child)
        mob2.children.append(child)
        mob1.children_count += 1
        mob2.children_count += 1
        mob1.fertility_meter = 0
        mob2.fertility_meter = 0
        mob1.fertility_ticks = 0
        mob2.fertility_ticks = 0
        self.mobs.append(child)
        self.factions[mob1.faction].append(child)
        self.add_notification(f"{child.name} born into faction {mob1.faction} as civilian.")


    def handle_zombie_swarming(self):
        zombies = [m for m in self.mobs if m.mob_type == "Zombie"]
        
        # Check for swarms of 10+ zombies in 10x10 grids
        for zombie in zombies:
            nearby_zombies = []
            for other_zombie in zombies:
                if abs(other_zombie.x - zombie.x) <= 5 and abs(other_zombie.y - zombie.y) <= 5:
                    nearby_zombies.append(other_zombie)
            
            if len(nearby_zombies) >= 10:
                # Find nearest king to target
                nearest_king = None
                min_distance = float('inf')
                for faction, king in self.king_cache.items():
                    distance = abs(king.x - zombie.x) + abs(king.y - zombie.y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_king = king
                
                if nearest_king:
                    # Set swarm target for all nearby zombies
                    for swarm_zombie in nearby_zombies:
                        swarm_zombie.target_attack_pos = (nearest_king.x, nearest_king.y)
                    
                    # Check if any zombie touches faction border
                    king_faction = nearest_king.faction
                    territory = self.get_faction_territory(king_faction)
                    border_tiles = self.get_border_tiles(king_faction)
                    
                    for swarm_zombie in nearby_zombies:
                        zombie_pos = (swarm_zombie.x, swarm_zombie.y)
                        for border_pos in border_tiles:
                            if abs(zombie_pos[0] - border_pos[0]) <= 1 and abs(zombie_pos[1] - border_pos[1]) <= 1:
                                self.alert_warriors(king_faction, zombie_pos)
                                self.add_notification(f"Zombie swarm threatens {king_faction}! Warriors alerted!")
                                break


    def handle_fights(self):
        fought_pairs = set()
        for mob1 in self.mobs:
            if mob1.health <= 0:
                continue
            if mob1.mob_type == "Human" and mob1.faction is None:
                continue
            for pos in self.get_adjacent_positions((mob1.x, mob1.y)):
                for mob2 in self.tile_mobs.get(pos, []):
                    if mob2 == mob1 or mob2.health <= 0:
                        continue
                    
                    # Humans fighting other humans of different factions
                    if mob1.mob_type == "Human" and mob2.mob_type == "Human":
                        if mob1.faction == mob2.faction:
                            continue
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)
                    
                    # Bear attacks humans logic
                    elif mob1.mob_type == "Bear" and mob2.mob_type == "Human":
                        if mob2.job in ("guard", "warrior"):
                            pair = tuple(sorted([mob1.name, mob2.name]))
                            if pair in fought_pairs:
                                continue
                            fought_pairs.add(pair)
                            self.resolve_fight(mob1, mob2)
                        elif mob2.job == "civilian" or mob2.faction is None:
                            continue
                    elif mob2.mob_type == "Bear" and mob1.mob_type == "Human":
                        if mob1.job in ("guard", "warrior"):
                            pair = tuple(sorted([mob1.name, mob2.name]))
                            if pair in fought_pairs:
                                continue
                            fought_pairs.add(pair)
                            self.resolve_fight(mob1, mob2)
                        elif mob1.job == "civilian" or mob1.faction is None:
                            continue

                    # Zombie attacks humans
                    elif mob1.mob_type == "Zombie" and mob2.mob_type == "Human":
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)
                    elif mob2.mob_type == "Zombie" and mob1.mob_type == "Human":
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)
                    
                    # Warriors/Guards vs Zombies
                    elif mob1.mob_type == "Human" and mob1.job in ("guard", "warrior") and mob2.mob_type == "Zombie":
                        pair = tuple(sorted([mob1.name, mob2.name]))
                        if pair in fought_pairs:
                            continue
                        fought_pairs.add(pair)
                        self.resolve_fight(mob1, mob2)


    def resolve_fight(self, mob1, mob2):
        strength_map = {
            "civilian": 1,
            "guard": 4,
            "warrior": 3,
            "bear": 5,
            "zombie": 2
        }
        s1 = strength_map.get(mob1.job, 1) * mob1.health
        s2 = strength_map.get(mob2.job, 1) * mob2.health
        if s1 == s2:
            winner, loser = (mob1, mob2) if random.choice([True, False]) else (mob2, mob1)
        elif s1 > s2:
            winner, loser = mob1, mob2
        else:
            winner, loser = mob2, mob1
        damage = max(10, winner.health // 2)
        loser.health -= damage
        if loser.health < 0:
            loser.health = 0
            winner.kills += 1
            if loser.mob_type == "Human" and loser.job == "civilian" and loser.faction:
                self.alert_warriors(loser.faction, (loser.x, loser.y))
        self.add_notification(f"Fight: {winner.name} ({winner.job}) won vs {loser.name} ({loser.job}), dealt {damage} damage.")


    def alert_warriors(self, faction, pos):
        for mob in self.factions.get(faction, []):
            if mob.job == "warrior":
                mob.alerted = True
                mob.target_attack_pos = pos


    def clear_attack_alerts(self):
        for mob in self.mobs:
            if mob.mob_type == "Human":
                mob.alerted = False
                mob.target_attack_pos = None


    def handle_neutral_faction_creation(self):
        for mob in list(self.mobs):
            if mob.mob_type != "Human" or mob.faction is not None:
                continue
            mob.neutral_ticks += 1
            if mob.neutral_ticks >= 50:
                nearby = [other for other in self.mobs if other.mob_type == "Human" and other.faction is None and abs(other.x - mob.x) <= 5 and abs(other.y - mob.y) <= 5]
                if nearby:
                    faction_name = f"Faction_{mob.name}"
                    for h in nearby:
                        h.faction = faction_name
                        h.neutral_ticks = 0
                        h.job = "civilian"
                    self.factions[faction_name] = nearby
                    for dx in range(-5,6):
                        for dy in range(-5,6):
                            x,y = mob.x+dx, mob.y+dy
                            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                                if self.claimed_land.get((x,y)) not in ("mountain","rock"):
                                    self.claimed_land[(x,y)] = faction_name
                    self.add_notification(f"{mob.name} started new faction {faction_name}.")
                    self.assign_king(faction_name)
                    self.update_faction_colors()


    def assign_king(self, faction_name):
        members = self.factions.get(faction_name, [])
        if not members:
            return
        king = max(members, key=lambda m: m.age)
        king.is_king = True
        king.health = min(king.health*2, 100)
        self.add_notification(f"{king.name} is the king of {faction_name}.")


    def promote_guards(self):
        for faction, members in self.factions.items():
            guards = [m for m in members if m.job == "guard"]
            civilians = [m for m in members if m.job == "civilian" and m.health > 50]
            needed = 10 - len(guards)
            if needed > 0 and civilians:
                civilians.sort(key=lambda m: m.health, reverse=True)
                for civ in civilians[:needed]:
                    civ.job = "guard"
                    civ.health = min(civ.health + 30, 100)
                    self.add_notification(f"{civ.name} promoted to guard in {faction}.")
            guards.sort(key=lambda m: m.health)
            if len(guards) > 10:
                for g in guards[10:]:
                    g.job = "civilian"
                    self.add_notification(f"{g.name} demoted to civilian in {faction}.")


    def assign_warriors(self):
        for faction, members in self.factions.items():
            warriors = [m for m in members if m.job == "warrior"]
            civilians = [m for m in members if m.job == "civilian"]
            total = len(members)
            max_warriors = max(total // 2, 0)
            needed = max_warriors - len(warriors)
            if needed > 0 and civilians:
                civilians.sort(key=lambda m: (m.kills, m.health), reverse=True)
                for civ in civilians[:needed]:
                    civ.job = "warrior"
                    civ.health = min(civ.health + 10, 100)
                    self.add_notification(f"{civ.name} assigned as warrior in {faction}.")
            if len(warriors) > max_warriors:
                for w in warriors[max_warriors:]:
                    w.job = "civilian"
                    self.add_notification(f"{w.name} demoted to civilian in {faction}.")


    def move_mobs_advanced(self):
        for mob in self.mobs:
            if mob.health <= 0:
                continue
            if mob.mob_type == "Bear":
                self.move_bear_ai(mob)
            elif mob.mob_type == "Human":
                if mob.job == "civilian":
                    self.move_civilian_ai(mob)
                elif mob.job == "guard":
                    self.move_guard_ai(mob)
                elif mob.job == "warrior":
                    self.move_warrior_ai(mob)
            elif mob.mob_type == "Zombie":
                self.move_zombie_ai(mob)


    def move_civilian_ai(self, mob):
        # Civilians run from zombies
        nearby_zombies = [m for m in self.mobs if m.mob_type == "Zombie" and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3]
        if nearby_zombies:
            closest_zombie = min(nearby_zombies, key=lambda z: abs(z.x - mob.x) + abs(z.y - mob.y))
            self.move_away_from(mob, (closest_zombie.x, closest_zombie.y))
            return


        if mob.faction is None:
            self.random_move(mob)
            claim = self.claimed_land.get((mob.x, mob.y))
            if claim and claim not in ("mountain", "rock", "dead_tile"):
                mob.faction = claim
                self.factions.setdefault(claim,[]).append(mob)
                self.add_notification(f"{mob.name} joined faction {claim} as civilian.")
        else:
            territory = self.get_faction_territory(mob.faction)
            moves = self.get_valid_moves(mob, [(0,1),(0,-1),(1,0),(-1,0)])
            moves = [d for d in moves if (mob.x+d[0], mob.y+d[1]) in territory]
            if moves:
                dx, dy = random.choice(moves)
                mob.x += dx
                mob.y += dy
            if random.random() < 0.01:
                self.try_claim_land(mob)


    def move_guard_ai(self, mob):
        # Guards run from zombies unless protecting king
        nearby_zombies = [m for m in self.mobs if m.mob_type == "Zombie" and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3]
        king = self.king_cache.get(mob.faction)
        
        if nearby_zombies and king:
            king_distance = abs(mob.x - king.x) + abs(mob.y - king.y)
            if king_distance > 2:  # If not close to king, run from zombies
                closest_zombie = min(nearby_zombies, key=lambda z: abs(z.x - mob.x) + abs(z.y - mob.y))
                self.move_away_from(mob, (closest_zombie.x, closest_zombie.y))
                return


        if king is None or king == mob:
            self.move_civilian_ai(mob)
            return
        dist = abs(mob.x - king.x) + abs(mob.y - king.y)
        if dist > 3:
            self.move_towards(mob, (king.x, king.y))
        else:
            moves = self.get_valid_moves(mob, [(0,1),(0,-1),(1,0),(-1,0)])
            moves = [d for d in moves if abs(mob.x + d[0] - king.x)+abs(mob.y + d[1] - king.y) <= 3]
            if moves:
                dx, dy = random.choice(moves)
                mob.x += dx
                mob.y += dy


    def move_warrior_ai(self, mob):
        # Warriors actively hunt zombies and enemies
        territory = self.get_faction_territory(mob.faction)
        border_tiles = self.get_border_tiles(mob.faction)
        x, y = mob.x, mob.y


        if mob.alerted and mob.target_attack_pos:
            self.move_towards(mob, mob.target_attack_pos, avoid_warriors=True)
            if abs(mob.x - mob.target_attack_pos[0]) <= 1 and abs(mob.y - mob.target_attack_pos[1]) <= 1:
                mob.alerted = False
                mob.target_attack_pos = None
            return


        # Prioritize zombies over other enemies
        zombies = self.scan_for_zombies(mob, 5)
        if zombies:
            nearest_zombie = min(zombies, key=lambda m: abs(m.x - x) + abs(m.y - y))
            self.move_towards(mob, (nearest_zombie.x, nearest_zombie.y), avoid_warriors=True)
            return


        enemies = self.scan_for_enemies(mob, 3)
        if enemies:
            nearest_enemy = min(enemies, key=lambda m: abs(m.x - x) + abs(m.y - y))
            self.move_towards(mob, (nearest_enemy.x, nearest_enemy.y), avoid_warriors=True)
            return


        if (x,y) not in border_tiles:
            if border_tiles:
                closest_border = min(border_tiles, key=lambda p: abs(p[0]-x) + abs(p[1]-y))
                self.move_towards(mob, closest_border, avoid_warriors=True)
            else:
                self.move_civilian_ai(mob)
            return


        nbr_moves = [(0,1),(0,-1),(1,0),(-1,0)]
        border_adjacent = []
        for dx, dy in nbr_moves:
            nx, ny = x+dx, y+dy
            if (nx, ny) in border_tiles:
                blocked = False
                for m in self.tile_mobs.get((nx, ny), []):
                    if m != mob and m.faction == mob.faction and m.job == "warrior":
                        blocked = True
                        break
                if not blocked:
                    border_adjacent.append((nx, ny))
        if border_adjacent:
            nx, ny = random.choice(border_adjacent)
            mob.x, mob.y = nx, ny
        else:
            moves = self.get_valid_moves(mob, nbr_moves)
            moves = [d for d in moves if (mob.x + d[0], mob.y + d[1]) in territory]
            if moves:
                dx, dy = random.choice(moves)
                mob.x += dx
                mob.y += dy

    def move_zombie_ai(self, mob):
        # If zombie has a target from swarming, move towards it
        if hasattr(mob, 'target_attack_pos') and mob.target_attack_pos:
            self.move_towards(mob, mob.target_attack_pos)
            return


        # Look for nearby humans to chase
        nearby_humans = [m for m in self.mobs if m.mob_type == "Human" and abs(m.x - mob.x) <= 5 and abs(m.y - mob.y) <= 5]
        if nearby_humans:
            # Prefer civilians over warriors/guards
            civilians = [h for h in nearby_humans if h.job == "civilian"]
            if civilians:
                target = min(civilians, key=lambda h: abs(h.x - mob.x) + abs(h.y - mob.y))
            else:
                target = min(nearby_humans, key=lambda h: abs(h.x - mob.x) + abs(h.y - mob.y))
            self.move_towards(mob, (target.x, target.y))
            return


        # Look for other zombies to group with
        nearby_zombies = [m for m in self.mobs if m.mob_type == "Zombie" and m != mob and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3]
        if nearby_zombies and len(nearby_zombies) < 5:  # Don't overcrowd
            closest_zombie = min(nearby_zombies, key=lambda z: abs(z.x - mob.x) + abs(z.y - mob.y))
            self.move_towards(mob, (closest_zombie.x, closest_zombie.y))
            return


        # Random movement
        self.random_move(mob)


    def move_bear_ai(self, mob):
        closest_mountain = None
        min_dist = 9999
        for mx, my in self.mountains:
            dist = abs(mx - mob.x) + abs(my - mob.y)
            if dist < min_dist:
                min_dist = dist
                closest_mountain = (mx, my)


        if closest_mountain and min_dist > 5:
            self.move_towards(mob, closest_mountain)
            return


        enemies = self.scan_for_humans_3x3(mob)


        if not enemies:
            self.random_move_near(mob, closest_mountain)
            return


        for h in enemies:
            if h.job in ("guard","warrior"):
                self.move_towards(mob, (h.x, h.y))
                return


        closest_h = min(enemies, key=lambda m: abs(m.x - mob.x) + abs(m.y - mob.y))
        dx = mob.x - closest_h.x
        dy = mob.y - closest_h.y
        move_options = self.get_valid_moves(mob, [(0,1),(0,-1),(1,0),(-1,0)])
        if not move_options:
            return
        def dist_if_move(d):
            nx, ny = mob.x + d[0], mob.y + d[1]
            return abs(nx - closest_h.x) + abs(ny - closest_h.y)
        move_options.sort(key=dist_if_move, reverse=True)
        mob.x += move_options[0][0]
        mob.y += move_options[0][1]


    def scan_for_enemies(self, mob, radius):
        enemies = []
        for other in self.mobs:
            if other == mob or other.health <= 0:
                continue
            if abs(other.x - mob.x) <= radius and abs(other.y - mob.y) <= radius:
                if mob.mob_type == "Human" and other.mob_type == "Human":
                    if mob.faction != other.faction:
                        enemies.append(other)
                elif mob.mob_type == "Human" and other.mob_type == "Bear":
                    enemies.append(other)
                elif mob.mob_type == "Bear" and other.mob_type == "Human":
                    enemies.append(other)
        return enemies


    def scan_for_zombies(self, mob, radius):
        return [m for m in self.mobs if m.mob_type == "Zombie" and abs(m.x - mob.x) <= radius and abs(m.y - mob.y) <= radius and m.health > 0]


    def scan_for_humans_3x3(self, mob):
        return [m for m in self.mobs if m.mob_type == "Human" and abs(m.x - mob.x) <= 3 and abs(m.y - mob.y) <= 3 and m.health > 0]


    def get_faction_territory(self, faction):
        return set(pos for pos, f in self.claimed_land.items() if f == faction)


    def get_border_tiles(self, faction):
        territory = self.get_faction_territory(faction)
        border_tiles = set()
        for x, y in territory:
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if (nx, ny) not in territory:
                    border_tiles.add((x,y))
                    break
        return border_tiles


    def move_towards(self, mob, target, avoid_warriors=False):
        tx, ty = target
        cx, cy = mob.x, mob.y
        options = []
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        for dx,dy in directions:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.claimed_land.get((nx, ny)) in ("mountain","rock"):
                    continue
                occupied_by = next((m for m in self.mobs if m.x == nx and m.y == ny and m != mob), None)
                if occupied_by:
                    if avoid_warriors and occupied_by.job == "warrior" and occupied_by.faction == mob.faction:
                        continue
                    else:
                        continue
                dist_before = abs(cx - tx) + abs(cy - ty)
                dist_after = abs(nx - tx) + abs(ny - ty)
                if dist_after < dist_before:
                    options.append((nx, ny))
        if options:
            nx, ny = random.choice(options)
            mob.x, mob.y = nx, ny
        else:
            if mob.mob_type == "Human" and mob.faction:
                territory = self.get_faction_territory(mob.faction)
                valid_moves = self.get_valid_moves(mob, directions)
                valid_moves = [d for d in valid_moves if (mob.x + d[0], mob.y + d[1]) in territory]
                if valid_moves:
                    dx, dy = random.choice(valid_moves)
                    mob.x += dx
                    mob.y += dy
            else:
                self.random_move(mob)


    def move_away_from(self, mob, threat_pos):
        tx, ty = threat_pos
        cx, cy = mob.x, mob.y
        options = []
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        for dx,dy in directions:
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.claimed_land.get((nx, ny)) in ("mountain","rock"):
                    continue
                occupied_by = next((m for m in self.mobs if m.x == nx and m.y == ny and m != mob), None)
                if occupied_by:
                    continue
                dist_before = abs(cx - tx) + abs(cy - ty)
                dist_after = abs(nx - tx) + abs(ny - ty)
                if dist_after > dist_before:  # Moving away increases distance
                    options.append((nx, ny))
        if options:
            nx, ny = random.choice(options)
            mob.x, mob.y = nx, ny
        else:
            self.random_move(mob)


    def random_move(self, mob):
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        moves = self.get_valid_moves(mob, directions)
        if moves:
            dx, dy = random.choice(moves)
            mob.x += dx
            mob.y += dy


    def random_move_near(self, mob, point):
        if point is None:
            self.random_move(mob)
            return
        px, py = point
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        moves = self.get_valid_moves(mob, directions)
        moves = [d for d in moves if abs(mob.x + d[0] - px) <= 10 and abs(mob.y + d[1] - py) <= 10]
        if moves:
            dx, dy = random.choice(moves)
            mob.x += dx
            mob.y += dy
        else:
            self.random_move(mob)


    def get_valid_moves(self, mob, directions):
        valid = []
        for dx, dy in directions:
            nx, ny = mob.x + dx, mob.y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if self.claimed_land.get((nx, ny)) in ("mountain", "rock"):
                    continue
                if any(m.x == nx and m.y == ny for m in self.mobs if m != mob):
                    continue
                valid.append((dx, dy))
        return valid


    def try_claim_land(self, mob):
        if mob.faction is None:
            return
        if mob.job not in ("civilian", "guard"):
            return
        adjacent = [(mob.x+dx, mob.y+dy) for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]]
        claimed = False
        for x, y in adjacent:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                current_claim = self.claimed_land.get((x,y))
                if current_claim is None or current_claim == "dead_tile":
                    if (x,y) not in self.mountains and (x,y) not in self.rocks:
                        if random.random() < 0.02:
                            self.claimed_land[(x,y)] = mob.faction
                            claimed = True
                            self.add_notification(f"{mob.name} ({mob.job}) expanded territory at ({x},{y}).")
        if claimed and self.show_claims:
            self.draw_claims_overlay()


    def spawn_human(self):
        empty_tiles = [(x,y) for x in range(self.grid_size) for y in range(self.grid_size)
                       if (not any(m.x==x and m.y==y for m in self.mobs) and self.claimed_land.get((x,y)) not in ("dead_tile","mountain","rock"))]
        if not empty_tiles:
            return
        x,y = random.choice(empty_tiles)
        name = f"Human{len(self.mobs)+1}"
        human = Mob(x,y,name=name,mob_type="Human",faction=None, job="civilian")
        human.max_children = random.randint(1, 3)
        self.mobs.append(human)
        self.add_notification(f"{name} spawned at ({x},{y}) as civilian.")

    def spawn_bear(self):
        if not self.mountains:
            self.add_notification("No mountains to spawn bears near.")
            return
        mx, my = random.choice(list(self.mountains))
        for _ in range(100):
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            x, y = mx+dx, my+dy
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                if self.claimed_land.get((x,y)) in ("mountain","rock"):
                    continue
                if any(m.x == x and m.y == y for m in self.mobs):
                    continue
                name = f"Bear{len([m for m in self.mobs if m.mob_type == 'Bear'])+1}"
                bear = Mob(x,y,name=name,mob_type="Bear", faction=None, job="bear", health=100)
                self.mobs.append(bear)
                self.add_notification(f"{name} spawned near mountain at ({x},{y}).")
                return
        self.add_notification("Failed to spawn bear near mountain.")


    def update_population_display(self):
        humans = [m for m in self.mobs if m.mob_type == "Human"]
        zombies = [m for m in self.mobs if m.mob_type == "Zombie"]
        bears = [m for m in self.mobs if m.mob_type == "Bear"]
        self.population_var.set(f"Humans: {len(humans)} | Zombies: {len(zombies)} | Bears: {len(bears)}")


    def update_canvas_mobs(self):
        for mob in list(self.mob_rects.keys()):
            if mob not in self.mobs:
                self.canvas.delete(self.mob_rects[mob])
                del self.mob_rects[mob]
                if mob in self.faction_dot_ids:
                    self.canvas.delete(self.faction_dot_ids[mob])
                    del self.faction_dot_ids[mob]
                if mob in self.king_marker_ids:
                    self.canvas.delete(self.king_marker_ids[mob])
                    del self.king_marker_ids[mob]


        for mob in self.mobs:
            px1 = mob.x * self.cell_size + 1
            py1 = mob.y * self.cell_size + 1
            px2 = (mob.x + 1) * self.cell_size - 1
            py2 = (mob.y + 1) * self.cell_size - 1


            if mob not in self.mob_rects:
                color = "brown"
                if mob.mob_type == "Bear":
                    color = "black"
                elif mob.mob_type == "Zombie":
                    color = "purple"
                else:
                    if mob.job == "civilian":
                        color = "sienna"
                    elif mob.job == "guard":
                        color = "orange"
                    elif mob.job == "warrior":
                        color = "red"
                rect_id = self.canvas.create_rectangle(px1, py1, px2, py2, fill=color, outline="")
                self.mob_rects[mob] = rect_id
            else:
                rect_id = self.mob_rects[mob]
                coords = self.canvas.coords(rect_id)
                desired = [px1, py1, px2, py2]
                if coords != desired:
                    self.canvas.coords(rect_id, *desired)


            if mob.mob_type == "Human" and mob.faction:
                ccolor = self.faction_colors.get(mob.faction, "white")
                cx = mob.x * self.cell_size + self.cell_size // 2
                cy = mob.y * self.cell_size + self.cell_size // 2
                if mob not in self.faction_dot_ids:
                    dot_id = self.canvas.create_oval(cx, cy, cx+2, cy+2, fill=ccolor, outline=ccolor)
                    self.faction_dot_ids[mob] = dot_id
                else:
                    self.canvas.coords(self.faction_dot_ids[mob], cx, cy, cx+2, cy+2)
                    self.canvas.itemconfig(self.faction_dot_ids[mob], fill=ccolor, outline=ccolor)
            else:
                if mob in self.faction_dot_ids:
                    self.canvas.delete(self.faction_dot_ids[mob])
                    del self.faction_dot_ids[mob]


            if mob.is_king:
                rid = self.mob_rects[mob]
                coords = self.canvas.coords(rid)
                x1, y1, x2, y2 = coords
                if mob not in self.king_marker_ids:
                    marker_id = self.canvas.create_rectangle(x1, y1, (x1 + x2) / 2, y2, fill='yellow', stipple='gray25', outline='')
                    self.king_marker_ids[mob] = marker_id
                else:
                    self.canvas.coords(self.king_marker_ids[mob], x1, y1, (x1 + x2) / 2, y2)
                    self.canvas.itemconfig(self.king_marker_ids[mob], state='normal')
            else:
                if mob in self.king_marker_ids:
                    self.canvas.itemconfig(self.king_marker_ids[mob], state='hidden')


        if self.show_claims:
            self.draw_claims_overlay()
        else:
            self.clear_claims_overlay()


    def draw_mobs(self, initial=False):
        if initial:
            for mob in self.mobs:
                px1 = mob.x * self.cell_size + 1
                py1 = mob.y * self.cell_size + 1
                px2 = (mob.x+1) * self.cell_size - 1
                py2 = (mob.y+1) * self.cell_size - 1


                color = "brown"
                if mob.mob_type == "Bear":
                    color = "black"
                elif mob.mob_type == "Zombie":
                    color = "purple"
                else:
                    if mob.job == "civilian":
                        color = "sienna"
                    elif mob.job == "guard":
                        color = "orange"
                    elif mob.job == "warrior":
                        color = "red"


                rect_id = self.canvas.create_rectangle(px1, py1, px2, py2, fill=color, outline="")
                self.mob_rects[mob] = rect_id


                if mob.mob_type == "Human" and mob.faction:
                    ccolor = self.faction_colors.get(mob.faction, "white")
                    cx = mob.x * self.cell_size + self.cell_size // 2
                    cy = mob.y * self.cell_size + self.cell_size // 2
                    dot_id = self.canvas.create_oval(cx, cy, cx+2, cy+2, fill=ccolor, outline=ccolor)
                    self.faction_dot_ids[mob] = dot_id


                if mob.is_king:
                    marker_id = self.canvas.create_rectangle(px1, py1, (px1+px2)/2, py2, fill='yellow', stipple='gray25', outline='')
                    self.king_marker_ids[mob] = marker_id


            if self.show_claims:
                self.draw_claims_overlay()


    def draw_claims_overlay(self):
        self.clear_claims_overlay()
        self.update_faction_colors()
        for (x, y), faction in self.claimed_land.items():
            if faction == "dead_tile":
                color = "#bbbbbb"
            elif faction == "mountain" or faction == "rock":
                continue
            else:
                color = self.faction_colors.get(faction, "#000000")
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            rid = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", stipple="gray25")
            self.claim_overlay_ids.append(rid)


    def clear_claims_overlay(self):
        for rid in self.claim_overlay_ids:
            self.canvas.delete(rid)
        self.claim_overlay_ids.clear()


    def update_faction_colors(self):
        factions = sorted(self.factions.keys())
        for i, fn in enumerate(factions):
            if fn not in self.faction_colors:
                self.faction_colors[fn] = self.faction_base_colors[i % len(self.faction_base_colors)]


    def toggle_claims_display(self, event=None):
        self.show_claims = not self.show_claims
        if self.show_claims:
            self.add_notification("Showing faction land claims.")
            self.draw_claims_overlay()
        else:
            self.add_notification("Hiding faction land claims.")
            self.clear_claims_overlay()


    def on_mouse_click(self, event):
        clicked = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked:
            mob = None
            for m, cid in self.mob_rects.items():
                if cid == item:
                    mob = m
                    break
            if mob:
                self.show_mob_panel(mob)
                break


    def show_mob_panel(self, mob):
        win = tk.Toplevel(self)
        win.title(f"{mob.name} info")
        faction = mob.faction or "Neutral"
        job = getattr(mob, 'job', 'unknown')
        txt = (f"Name: {mob.name}\nType: {mob.mob_type}\nJob: {job}\nFaction: {faction}"
               f"\nAge: {mob.age} years\nHealth: {mob.health}\nKills: {mob.kills}")
        
        if mob.mob_type == "Human":
            txt += f"\nFertility: {mob.fertility_meter}%"
            txt += f"\nChildren: {mob.children_count}/{mob.max_children}"
        
        if mob.parents:
            txt += "\nParents: " + ", ".join(p.name for p in mob.parents)
        else:
            txt += "\nParents: Unknown"
        if mob.children:
            txt += "\nChildren: " + ", ".join(c.name for c in mob.children)
        else:
            txt += "\nChildren: None"
        if mob.is_king:
            txt += "\nStatus: King"
        label = tk.Label(win, text=txt, font=("Arial", 12), justify=tk.LEFT)
        label.pack(padx=10, pady=10)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=5)

    def toggle_faction_panel(self, event=None):
        if self.faction_panel_visible:
            self.faction_panel_frame.pack_forget()
            self.faction_panel_visible = False
        else:
            self.faction_panel_frame.pack(side=tk.LEFT, fill=tk.Y)
            self.faction_panel_visible = True
            self.update_faction_panel()


    def update_faction_panel(self):
        for w in self.faction_panel_inner.winfo_children():
            w.destroy()
        for faction, members in self.factions.items():
            if not members:
                continue
            lbl = tk.Label(self.faction_panel_inner, text=f"Faction: {faction} ({len(members)}/{self.max_faction_size})", font=("Arial", 14, "bold"), bg="lightgrey")
            lbl.pack(anchor="w", padx=10, pady=(10,2))
            for m in members:
                status_text = f"{m.name} ({m.job})"
                if m.is_king:
                    status_text += " [KING]"
                if m.mob_type == "Human":
                    status_text += f" F:{m.fertility_meter}%"
                b = tk.Button(self.faction_panel_inner, text=status_text, anchor="w", command=lambda mob=m: self.show_mob_panel(mob))
                b.pack(fill=tk.X, padx=20, pady=1)


    def handle_king_death(self, faction_name):
        members = self.factions.get(faction_name, [])
        if not members:
            self.remove_claimed_land_for_faction(faction_name)
            self.add_notification(f"Faction {faction_name} has died out. Territory unclaimed.")
            return
        candidates = []
        for m in members:
            if m.parents:
                for p in m.parents:
                    if p.is_king and p.faction == faction_name:
                        candidates.append(m)
        if candidates:
            new_king = max(candidates, key=lambda m: m.age)
        else:
            new_king = random.choice(members)
        new_king.is_king = True
        new_king.health = min(new_king.health*2, 100)
        self.add_notification(f"{new_king.name} is the new king of {faction_name}.")


    def remove_claimed_land_for_faction(self, faction_name):
        to_remove = [pos for pos, f in self.claimed_land.items() if f == faction_name]
        for pos in to_remove:
            del self.claimed_land[pos]
        if self.show_claims:
            self.draw_claims_overlay()


    def get_adjacent_positions(self, pos):
        x, y = pos
        candidates = []
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                candidates.append((nx, ny))
        return candidates


if __name__ == "__main__":
    app = GreenGridGame()
    app.mainloop()
