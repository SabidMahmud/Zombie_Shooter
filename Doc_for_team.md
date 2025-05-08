

---

# **Zombie Shooter 3D Game - Documentation (Detailed Customization Guide)**

This documentation provides a thorough overview of the game mechanics and how to customize the gameplay.

---

## **Game Setup and Customization**

### **1. Game States and Player Stats**

The game operates on three core states: **MENU**, **PLAYING**, and **GAME\_OVER**. These states control the flow of the game.

#### **Customizing Game States:**

To change the behavior of these states (e.g., adding new states or modifying transitions):

* Modify the `game_state` variable to switch between different states.
* For instance, if you want to add a **PAUSE** state, simply define it:

  ```python
  PAUSE = 3
  game_state = PAUSE  # To switch to pause state
  ```

#### **Customizing Player Health and Ammo:**

To modify the starting health and ammo of the player, adjust the following values in the `init_game()` function:

```python
def init_game():
    """Initialize or reset the game to starting state"""
    global player_pos, player_angle, player_health, player_ammo, player_score
    global zombies, boss, obstacles, projectiles, zombie_kill_count, missed_shots
    global game_state

    # Reset player
    player_pos = [0, 30, 0]  # x, y, z
    player_angle = 0
    player_health = 1000  # Modify starting health here
    player_ammo = 1000    # Modify starting ammo here
    player_score = 0
    missed_shots = 0
```

* To **increase/decrease health**, change `player_health` to a higher or lower number (e.g., `player_health = 1500`).
* To **increase/decrease ammo**, modify `player_ammo`.

---

## **Obstacles**

The obstacles in the game are trees and rocks that are randomly placed within the game environment. These objects interact with the player’s movement and projectiles.

### **Customizing Number of Obstacles:**

To modify the number of trees and rocks generated in the game:

```python
num_trees = 15  # Modify number of trees
num_rocks = 10  # Modify number of rocks
```

* **More trees/rocks**: Increase the number values (e.g., `num_trees = 30`).
* **Fewer trees/rocks**: Decrease the number values.

### **Customizing Obstacle Size and Spacing:**

To change the size of the obstacles (trees and rocks):

```python
def generate_obstacles():
    """Place random trees and rocks on the field"""
    global obstacles
    obstacles = []
    
    safe_radius = 100  # Minimum safe distance from the player

    for _ in range(num_trees):
        while True:
            x = random.uniform(-field_size / 2 + 50, field_size / 2 - 50)
            z = random.uniform(-field_size / 2 + 50, field_size / 2 - 50)
            if math.sqrt(x * x + z * z) < safe_radius:
                continue
            overlap = False
            for ox, oz, otype, oradius in obstacles:
                if math.sqrt((x - ox) ** 2 + (z - oz) ** 2) < oradius + 30:  # Adjust spacing here (30)
                    overlap = True
                    break
            if not overlap:
                obstacles.append((x, z, OBSTACLE_TREE, 20))  # 20 = tree radius
                break

    for _ in range(num_rocks):
        while True:
            x = random.uniform(-field_size / 2 + 30, field_size / 2 - 30)
            z = random.uniform(-field_size / 2 + 30, field_size / 2 - 30)
            if math.sqrt(x * x + z * z) < safe_radius:
                continue
            overlap = False
            for ox, oz, otype, oradius in obstacles:
                if math.sqrt((x - ox) ** 2 + (z - oz) ** 2) < oradius + 35:  # Adjust spacing here (35)
                    overlap = True
                    break
            if not overlap:
                obstacles.append((x, z, OBSTACLE_ROCK, 20))  # 20 = rock radius
                break
```

* **Increase obstacle size**: Increase the `oradius` value for trees and rocks (e.g., `20` to `30`).
* **Decrease obstacle size**: Decrease the `oradius` value (e.g., `20` to `10`).

### **Customizing Obstacle Spacing:**

* Increase the gap between obstacles by increasing the values `30` and `35` in the collision checks for trees and rocks.

  ```python
  if math.sqrt((x - ox) ** 2 + (z - oz) ** 2) < oradius + 30:  # Spacing between obstacles
  ```

---

## **Zombies and Boss**

### **Zombie Behavior and Customization**

Zombies follow the player and cause damage if they collide with the player.

#### **Zombie Health and Speed:**

```python
zombie_health = 50  # Modify health here
zombie_speed = 2    # Modify speed here
```

* **Zombie health**: Increase `zombie_health` to make zombies more durable (e.g., `zombie_health = 100`).
* **Zombie speed**: Increase `zombie_speed` to make zombies faster (e.g., `zombie_speed = 3`).

#### **Zombie Damage:**

```python
zombie_damage = 10  # Modify zombie damage here
```

* To **increase zombie damage**, modify `zombie_damage` (e.g., `zombie_damage = 20`).

#### **Zombie Spawn Rate:**

```python
zombie_spawn_interval = 3000  # Interval in milliseconds
```

* To **spawn zombies more frequently**, decrease `zombie_spawn_interval` (e.g., `zombie_spawn_interval = 2000` for faster spawning).
* To **spawn zombies less frequently**, increase `zombie_spawn_interval`.

### **Boss Customization**

The boss has specific mechanics, such as health thresholds that determine if it will lose its limbs.

#### **Boss Health and Damage:**

```python
boss_max_health = 500   # Modify health here
boss_damage = 25        # Modify damage here
```

* **Boss health**: Increase the boss’s health for a more challenging fight (e.g., `boss_max_health = 1000`).
* **Boss damage**: Increase the boss’s damage for a harder encounter (e.g., `boss_damage = 50`).

#### **Boss Limb Loss:**

The boss loses its limbs depending on health thresholds. Modify the thresholds to control when the limbs fall off:

```python
def update_boss():
    """Update boss position, state and behavior"""
    if health <= boss_max_health / 3 and state != BOSS_CRITICAL:
        boss[4] = BOSS_CRITICAL  # Critical state, arms/legs may fall off
    elif health <= boss_max_health * 2/3 and state != BOSS_WOUNDED and state != BOSS_CRITICAL:
        boss[4] = BOSS_WOUNDED  # Wounded state, limbs may be damaged
```

* Modify the fractions `2/3` and `1/3` to change when the limbs fall off (e.g., change to `1/2` for the boss to lose limbs at half health).

---

## **Projectile Handling**

### **Projectile Speed and Damage:**

You can modify the projectile speed and damage by adjusting the following values:

```python
projectile_speed = 15       # Modify speed here
projectile_radius = 5       # Modify radius here
```

* **Projectile speed**: Increase `projectile_speed` for faster projectiles (e.g., `projectile_speed = 20`).
* **Projectile radius**: Increase `projectile_radius` for larger projectiles (e.g., `projectile_radius = 10`).

### **Projectile Owner:**

You can distinguish between player and boss projectiles:

```python
PROJECTILE_PLAYER = 0
PROJECTILE_BOSS = 1
```

* **Customize projectile behavior**: For example, modify `PROJECTILE_BOSS` behavior to create more powerful projectiles when fired by the boss.

### **Collision Detection for Projectiles:**

If you want to adjust the logic for projectile collisions, modify this block:

```python
def update_projectiles():
    """Update all projectiles and check for collisions"""
    global projectiles, zombies, boss, player_health, missed_shots
    
    projectiles_to_remove = []
    
    for i, proj in enumerate(projectiles):
        x, z, dx, dz, owner = proj
        
        # Update position
        new_x = x + dx
        new_z = z + dz
        
        # Check if out of bounds
        if (new_x < -field_size/2 or new_x > field_size/2 or
            new_z < -field_size/2 or new_z > field_size/2):
            projectiles_to_remove.append(i)
            if owner == PROJECTILE_PLAYER:
                missed_shots += 1
            continue
```

* To **change projectile behavior on collision**, modify the conditions inside `update_projectiles()` to customize what happens when projectiles hit zombies, rocks, or the boss.

---

## **Drawing Functions**

### **Customizing Drawing of Entities**

You can customize how entities like the player, zombies, and obstacles are drawn in the 3D world.

#### **Drawing the Player:**

```python
def draw_player():
    """Draw the player character"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 1, 0)
```

* **Modify player appearance**: Adjust the size of the player by changing the `player_radius` and `player_height` variables. To change the color, modify `glColor3f()`.

#### **Drawing the Boss:**

```python
def draw_boss():
    """Draw the boss zombie with visual state changes based on health"""
```

* **Modify the boss size and color** by adjusting the `glScalef()` and `glColor3f()` functions.
* Customize the boss appearance based on health (e.g., add more dramatic effects as the boss gets weaker).

#### **Drawing Obstacles:**

```python
def draw_obstacles():
    """Draw trees and rocks on the field"""
```

* **Customize obstacle appearance**: Modify `glColor3f()` for the colors and adjust the size of trees and rocks using `glScalef()`.

### **HUD Customization**

You can customize the heads-up display (HUD) to show player stats, ammo, and other information:

```python
def draw_hud():
    """Draw heads-up display with player info"""
```

* **Add new stats to the HUD**, like the number of zombies killed or a mini-map, by adding more `glBegin(GL_QUADS)` to draw additional UI elements.
* Modify the color and size of existing bars by adjusting `glColor3f()` and `glScalef()`.

---

---

