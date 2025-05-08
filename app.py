from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Camera-related variables
camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 600
VIEW_FIRST_PERSON = 0
VIEW_THIRD_PERSON = 1
current_view = VIEW_THIRD_PERSON

# Player variables
player_pos = [0, 0, 0]  # x, y, z
player_angle = 0  # in degrees
player_health = 1000
player_ammo = 1000
player_score = 0
player_radius = 20
player_height = 60
player_speed = 5
missed_shots = 0
last_shot_time = 0
shot_cooldown = 500  # milliseconds between shots

# Field and boundary variables
field_size = 800
wall_height = 100

# Obstacle variables
num_trees = 15
num_rocks = 10
obstacles = []  # Will store (x, z, type, radius) for each obstacle
OBSTACLE_TREE = 0
OBSTACLE_ROCK = 1

# Zombie variables
zombies = []  # Will store (x, z, angle, health, state) for each zombie
zombie_radius = 15
zombie_speed = 2
zombie_damage = 10
zombie_health = 50
zombie_spawn_timer = 0
zombie_spawn_interval = 3000  # milliseconds
zombie_kill_count = 0
wave_zombie_limit = 5

NORMAL_ZOMBIE_DAMAGE = zombie_health

# Boss variables
boss = None  # Will be (x, z, angle, health, state, projectile_timer) when spawned
boss_radius = 40
boss_speed = 1
boss_damage = 25
boss_max_health = 500
boss_health = boss_max_health
boss_projectile_cooldown = 2000  # milliseconds
BOSS_HEALTHY = 0
BOSS_WOUNDED = 1  # First threshold at 2/3 health
BOSS_CRITICAL = 2  # Second threshold at 1/3 health

# Projectile variables
projectiles = []  # Will store (x, z, dx, dz, owner) for each projectile
projectile_speed = 15
projectile_radius = 5
PROJECTILE_PLAYER = 0
PROJECTILE_BOSS = 1

# Time tracking
last_time = 0
time_delta = 0

def init_game():
    """Initialize or reset the game to starting state"""
    global player_pos, player_angle, player_health, player_ammo, player_score
    global zombies, boss, obstacles, projectiles, zombie_kill_count, missed_shots
    global game_state

    # Reset player
    player_pos = [0, 30, 0]  # x, y, z
    player_angle = 0
    player_health = 100
    player_ammo = 30
    player_score = 0
    missed_shots = 0
    
    # Clear entities
    zombies = []
    boss = None
    projectiles = []
    zombie_kill_count = 0
    
    # Generate obstacles
    generate_obstacles()
    
    # Set game state to playing
    game_state = PLAYING

def generate_obstacles():
    """Place random trees and rocks on the field"""
    global obstacles
    obstacles = []
    
    # Keep player area clear (radius of 100 units)
    safe_radius = 100
    
    # Generate trees
    for _ in range(num_trees):
        while True:
            x = random.uniform(-field_size/2 + 50, field_size/2 - 50)
            z = random.uniform(-field_size/2 + 50, field_size/2 - 50)
            
            # Check if too close to player start position
            if math.sqrt(x*x + z*z) < safe_radius:
                continue
                
            # Check if overlapping with existing obstacles
            overlap = False
            for ox, oz, otype, oradius in obstacles:
                if math.sqrt((x-ox)**2 + (z-oz)**2) < oradius + 30:  # 30 = tree radius + spacing
                    overlap = True
                    break
                    
            if not overlap:
                obstacles.append((x, z, OBSTACLE_TREE, 20))  # Trees have radius 20
                break
    
    # Generate rocks
    for _ in range(num_rocks):
        while True:
            x = random.uniform(-field_size/2 + 30, field_size/2 - 30)
            z = random.uniform(-field_size/2 + 30, field_size/2 - 30)
            
            # Check if too close to player start position
            if math.sqrt(x*x + z*z) < safe_radius:
                continue
                
            # Check if overlapping with existing obstacles
            overlap = False
            for ox, oz, otype, oradius in obstacles:
                # if math.sqrt((x-ox)**2 + (z-oz)**2) < oradius + 25:  # 25 = rock radius + spacing
                if math.sqrt((x-ox)**2 + (z-oz)**2) < oradius + 35:  # 35 = rock radius + spacing
                    overlap = True
                    break
                    
            if not overlap:
                obstacles.append((x, z, OBSTACLE_ROCK, 20))  # Rocks have radius 20
                break

def spawn_zombie():
    """Spawn a zombie at a random position outside player safe radius"""
    safe_radius = 150  # Minimum distance from player
    max_radius = 300   # Maximum distance from player
    
    # Generate random angle
    angle = random.uniform(0, 2 * math.pi)
    
    # Generate random distance between safe_radius and max_radius
    distance = random.uniform(safe_radius, max_radius)
    
    # Calculate position
    x = player_pos[0] + distance * math.cos(angle)
    z = player_pos[2] + distance * math.sin(angle)
    
    # Ensure zombie is within field boundaries
    x = max(min(x, field_size/2 - 20), -field_size/2 + 20)
    z = max(min(z, field_size/2 - 20), -field_size/2 + 20)
    
    # Add zombie: (x, z, angle, health, state)
    zombies.append([x, z, 0, zombie_health, 0])

def spawn_boss():
    """Spawn a boss zombie at a random position outside player safe radius"""
    global boss
    
    safe_radius = 200  # Boss spawns further away
    
    # Generate random angle
    angle = random.uniform(0, 2 * math.pi)
    
    # Generate position at safe_radius
    x = player_pos[0] + safe_radius * math.cos(angle)
    z = player_pos[2] + safe_radius * math.sin(angle)
    
    # Ensure boss is within field boundaries
    x = max(min(x, field_size/2 - 50), -field_size/2 + 50)
    z = max(min(z, field_size/2 - 50), -field_size/2 + 50)
    
    # Create boss: (x, z, angle, health, state, projectile_timer)
    boss = [x, z, 0, boss_max_health, BOSS_HEALTHY, 0]

def shoot_projectile(owner_type):
    """Create a new projectile"""
    global projectiles, player_ammo, missed_shots, last_shot_time
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    
    if owner_type == PROJECTILE_PLAYER:
        # Check ammo and cooldown
        if player_ammo <= 0 or (current_time - last_shot_time) < shot_cooldown:
            return
            
        # Decrease ammo and reset cooldown
        player_ammo -= 1
        last_shot_time = current_time
        
        # Calculate direction
        dx = math.sin(math.radians(player_angle))
        dz = -math.cos(math.radians(player_angle))
        
        # Create projectile at player position
        projectiles.append([
            player_pos[0], 
            player_pos[2], 
            dx * projectile_speed, 
            dz * projectile_speed, 
            PROJECTILE_PLAYER
        ])
        
    elif owner_type == PROJECTILE_BOSS and boss:
        # Calculate direction toward player
        dx = player_pos[0] - boss[0]
        dz = player_pos[2] - boss[1]
        
        # Normalize
        length = math.sqrt(dx*dx + dz*dz)
        if length > 0:
            dx /= length
            dz /= length
            
        # Create projectile at boss position
        projectiles.append([
            boss[0], 
            boss[1], 
            dx * projectile_speed * 0.7,  # Boss projectiles are slower
            dz * projectile_speed * 0.7, 
            PROJECTILE_BOSS
        ])

def check_collision(x, z, radius, exclude_player=False):
    """Check if a position collides with obstacles, walls or player"""
    # Check wall collisions
    if (x < -field_size/2 + radius or x > field_size/2 - radius or
        z < -field_size/2 + radius or z > field_size/2 - radius):
        return True
        
    # Check obstacle collisions
    for ox, oz, otype, oradius in obstacles:
        if math.sqrt((x-ox)**2 + (z-oz)**2) < radius + oradius:
            return True
    
    # Check player collision if not excluded
    if not exclude_player:
        if math.sqrt((x-player_pos[0])**2 + (z-player_pos[2])**2) < radius + player_radius:
            return True
    
    return False

def update_player():
    """Update player position based on input and handle collisions"""
    global player_pos
    
    # Store old position for collision reversion
    old_x, old_y, old_z = player_pos
    
    # Apply pending movements from key handlers
    pass  # Will be implemented in keyboardListener

def update_zombies():
    """Update all zombie positions and states"""
    global zombies, player_health, zombie_kill_count, player_score
    
    zombies_to_remove = []
    
    for i, zombie in enumerate(zombies):
        x, z, angle, health, state = zombie
        
        # Calculate direction to player
        dx = player_pos[0] - x
        dz = player_pos[2] - z
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dz /= distance
            
            # Calculate new angle toward player
            new_angle = math.degrees(math.atan2(dx, -dz)) % 360
            zombie[2] = new_angle
            
            # Calculate new position
            new_x = x + dx * zombie_speed
            new_z = z + dz * zombie_speed
            
            # Check collisions
            if not check_collision(new_x, new_z, zombie_radius):
                zombie[0] = new_x
                zombie[1] = new_z
                
        # Check if zombie hits player
        if distance < player_radius + zombie_radius:
            player_health -= zombie_damage * time_delta / 1000  # Damage over time
            
            # Visual feedback for hit would go here
            
        # Check if zombie is dead
        if health <= 0:
            zombies_to_remove.append(i)
            zombie_kill_count += 1
            player_score += 100
    
    # Remove dead zombies (in reverse order to avoid index shifting)
    for i in sorted(zombies_to_remove, reverse=True):
        zombies.pop(i)

def update_boss():
    """Update boss position, state and behavior"""
    global boss, player_health
    
    if not boss:
        return
        
    x, z, angle, health, state, projectile_timer = boss
    
    # Update boss state based on health
    if health <= boss_max_health / 3 and state != BOSS_CRITICAL:
        boss[4] = BOSS_CRITICAL
    elif health <= boss_max_health * 2/3 and state != BOSS_WOUNDED and state != BOSS_CRITICAL:
        boss[4] = BOSS_WOUNDED
    
    # Calculate direction to player
    dx = player_pos[0] - x
    dz = player_pos[2] - z
    distance = math.sqrt(dx*dx + dz*dz)
    
    if distance > 0:
        # Normalize direction
        dx /= distance
        dz /= distance
        
        # Calculate new angle toward player
        new_angle = math.degrees(math.atan2(dx, -dz)) % 360
        boss[2] = new_angle
        
        # Move toward player but keep some distance for ranged attacks
        if distance > 150:  # Boss prefers to keep some distance
            new_x = x + dx * boss_speed
            new_z = z + dz * boss_speed
            
            # Check collisions
            if not check_collision(new_x, new_z, boss_radius):
                boss[0] = new_x
                boss[1] = new_z
        
        # Check if boss hits player in melee range
        if distance < player_radius + boss_radius:
            player_health -= boss_damage * time_delta / 1000  # Damage over time
    
    # Update projectile timer
    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - projectile_timer > boss_projectile_cooldown:
        shoot_projectile(PROJECTILE_BOSS)
        boss[5] = current_time  # Reset timer

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
            
        # Check obstacle collisions
        if check_collision(new_x, new_z, projectile_radius, exclude_player=True):
            projectiles_to_remove.append(i)
            if owner == PROJECTILE_PLAYER:
                missed_shots += 1
            continue
            
        # Update position if no collision
        proj[0] = new_x
        proj[1] = new_z
        
        # Player projectile hits zombie or boss
        if owner == PROJECTILE_PLAYER:
            # Check zombie hits
            zombie_hit = False
            for j, zombie in enumerate(zombies):
                zx, zz = zombie[0], zombie[1]
                if math.sqrt((new_x-zx)**2 + (new_z-zz)**2) < projectile_radius + zombie_radius:
                    # zombies[j][3] -= 25  # Projectile damage
                    zombies[j][3] -= NORMAL_ZOMBIE_DAMAGE  # Projectile damage
                    projectiles_to_remove.append(i)
                    zombie_hit = True
                    break
                    
            # Check boss hit
            if not zombie_hit and boss:
                bx, bz = boss[0], boss[1]
                if math.sqrt((new_x-bx)**2 + (new_z-bz)**2) < projectile_radius + boss_radius:
                    boss[3] -= 25  # Projectile damage
                    projectiles_to_remove.append(i)
                    
        # Boss projectile hits player
        elif owner == PROJECTILE_BOSS:
            if math.sqrt((new_x-player_pos[0])**2 + (new_z-player_pos[2])**2) < projectile_radius + player_radius:
                player_health -= 15  # Boss projectile damage
                projectiles_to_remove.append(i)
    
    # Remove collided projectiles (in reverse order)
    for i in sorted(projectiles_to_remove, reverse=True):
        projectiles.pop(i)

def update_game_state():
    """Update game state based on conditions"""
    global game_state, zombie_kill_count, boss, zombie_spawn_timer
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    
    if game_state == PLAYING:
        # Check for game over condition
        if player_health <= 0:
            game_state = GAME_OVER
            return
            
        # Check if we need to spawn boss
        if zombie_kill_count >= wave_zombie_limit and boss is None:
            spawn_boss()
            
        # Check if boss is defeated
        if boss and boss[3] <= 0:
            boss = None
            player_score += 1000
            zombie_kill_count = 0  # Reset for next wave
            
        # Spawn zombies if no boss present
        if boss is None and len(zombies) < wave_zombie_limit:
            if current_time - zombie_spawn_timer > zombie_spawn_interval:
                spawn_zombie()
                zombie_spawn_timer = current_time

def update():
    """Main update function for game logic"""
    global time_delta, last_time
    
    # Calculate time delta
    current_time = glutGet(GLUT_ELAPSED_TIME)
    time_delta = current_time - last_time
    last_time = current_time
    
    if game_state == PLAYING:
        update_player()
        update_zombies()
        update_boss()
        update_projectiles()
        update_game_state()

def draw_grid():
    """Draw the floor grid"""
    grid_size = field_size
    cell_size = 50  # Size of each grid cell
    
    glColor3f(0.3, 0.3, 0.3)  # Dark gray for grid lines
    
    # Draw the base floor
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.6, 0.2)  # Green for grass
    glVertex3f(-grid_size/2, 0, -grid_size/2)
    glVertex3f(-grid_size/2, 0, grid_size/2)
    glVertex3f(grid_size/2, 0, grid_size/2)
    glVertex3f(grid_size/2, 0, -grid_size/2)
    glEnd()
    
    # Draw grid lines
    glBegin(GL_LINES)
    glColor3f(0.3, 0.3, 0.3)
    
    # Vertical lines (along Z-axis)
    for i in range(-int(grid_size/2), int(grid_size/2) + 1, cell_size):
        glVertex3f(i, 1, -grid_size/2)
        glVertex3f(i, 1, grid_size/2)
    
    # Horizontal lines (along X-axis)
    for i in range(-int(grid_size/2), int(grid_size/2) + 1, cell_size):
        glVertex3f(-grid_size/2, 1, i)
        glVertex3f(grid_size/2, 1, i)
    
    glEnd()

def draw_walls():
    """Draw boundary walls around the field"""
    glPushMatrix() # 1st er push matrix
    
    
    glColor3f(0.6, 0.3, 0.1)  # Brown color for walls
    
    wall_thickness = 20
    
    # North wall
    glPushMatrix()
    glTranslatef(0, wall_height/2, -field_size/2)
    glScalef(field_size + wall_thickness*2, wall_height, wall_thickness)
    glutSolidCube(1)
    glPopMatrix()
    
    # South wall
    glPushMatrix()
    glTranslatef(0, wall_height/2, field_size/2)
    glScalef(field_size + wall_thickness*2, wall_height, wall_thickness)
    glutSolidCube(1)
    glPopMatrix()
    
    # East wall
    glPushMatrix()
    glTranslatef(field_size/2, wall_height/2, 0)
    glScalef(wall_thickness, wall_height, field_size)
    glutSolidCube(1)
    glPopMatrix()
    
    # West wall
    glPushMatrix()
    glTranslatef(-field_size/2, wall_height/2, 0)
    glScalef(wall_thickness, wall_height, field_size)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix() # 1st er tar pop matrix

def draw_obstacles():
    """Draw trees and rocks on the field"""
    for x, z, obstacle_type, radius in obstacles:
        glPushMatrix()
        glTranslatef(x, 0, z)
        
        if obstacle_type == OBSTACLE_TREE:
            # Draw tree trunk
            glColor3f(0.6, 0.3, 0.1)  # Brown
            glPushMatrix()
            glTranslatef(0, 25, 0)
            glScalef(10, 50, 10)
            glutSolidCube(1)
            glPopMatrix()
            
            # Draw tree top

            glColor3f(0.0, 0.5, 0.0)  # Dark green
            glPushMatrix()
            glTranslatef(0, 60, 0)
            glRotatef(-90, 1, 0, 0)     # rotate cone from +Z into +Y
            glutSolidCone(30, 60, 10, 10)
            glPopMatrix()

            
        elif obstacle_type == OBSTACLE_ROCK:
            # Draw rock
            glColor3f(0.5, 0.5, 0.5)  # Gray
            glPushMatrix()
            glTranslatef(0, radius, 0)
            glutSolidSphere(radius, 10, 10)
            glPopMatrix()
            
        glPopMatrix()

def draw_player():
    """Draw the player character"""
    glPushMatrix()
    
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 1, 0)
    
    # Player body
    glColor3f(0.0, 0.0, 0.8)  # Blue
    glPushMatrix()
    glTranslatef(0, player_height/2 - 10, 0)
    glScalef(player_radius, player_height - 20, player_radius)
    glutSolidCube(1)
    glPopMatrix()
    
    # Player head
    glColor3f(0.8, 0.6, 0.5)  # Skin color
    glPushMatrix()
    glTranslatef(0, player_height - 10, 0)
    glutSolidSphere(10, 10, 10)
    glPopMatrix()
    
    # Gun
    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    glPushMatrix()
    glTranslatef(player_radius - 5, player_height - 25, player_radius - 5)
    glRotatef(90, 0, 1, 0)
    glScalef(5, 5, 20)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()

def draw_zombies():
    """Draw all zombies"""
    for x, z, angle, health, state in zombies:
        glPushMatrix()
        
        glTranslatef(x, 30, z)
        glRotatef(angle, 0, 1, 0)
        
        # Zombie body
        glColor3f(0.0, 0.8, 0.0)  # Green for zombies
        glPushMatrix()
        glTranslatef(0, 20, 0)
        glScalef(zombie_radius, 50, zombie_radius)
        glutSolidCube(1)
        glPopMatrix()
        
        # Zombie head
        glColor3f(0.0, 0.6, 0.0)  # Darker green
        glPushMatrix()
        glTranslatef(0, 55, 0)
        glutSolidSphere(15, 10, 10)
        glPopMatrix()
        
        # Arms
        glColor3f(0.0, 0.7, 0.0)
        
        # Left arm
        glPushMatrix()
        glTranslatef(-zombie_radius - 5, 30, 0)
        glRotatef(45, 0, 0, 1)
        glScalef(5, 30, 5)
        glutSolidCube(1)
        glPopMatrix()
        
        # Right arm
        glPushMatrix()
        glTranslatef(zombie_radius + 5, 30, 0)
        glRotatef(-45, 0, 0, 1)
        glScalef(5, 30, 5)
        glutSolidCube(1)
        glPopMatrix()
        
        # Health bar (red background)
        glPushMatrix()
        glTranslatef(0, 70, 0)
        glRotatef(-angle, 0, 1, 0)  # Counter-rotate to face camera
        
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-15, 0, 0)
        glVertex3f(15, 0, 0)
        glVertex3f(15, 5, 0)
        glVertex3f(-15, 5, 0)
        glEnd()
        
        # Health bar (green fill)
        health_pct = max(0, health / zombie_health)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-15, 0, 0)
        glVertex3f(-15 + 30 * health_pct, 0, 0)
        glVertex3f(-15 + 30 * health_pct, 5, 0)
        glVertex3f(-15, 5, 0)
        glEnd()
        
        glPopMatrix()
        
        glPopMatrix()


# def draw_boss():
#     """Draw the boss zombie with visual state changes based on health"""
#     if not boss:
#         return
        
#     x, z, angle, health, state, _ = boss
    
#     glPushMatrix()
    
#     glTranslatef(x, 40, z)
#     glRotatef(angle, 0, 1, 0)
    
#     # Boss body
#     glColor3f(0.8, 0.0, 0.0)  # Red for boss
#     glPushMatrix()
#     glTranslatef(0, 40, 0)
#     glScalef(boss_radius, 80, boss_radius)
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Boss head
#     glColor3f(0.6, 0.0, 0.0)  # Darker red
#     glPushMatrix()
#     glTranslatef(0, 90, 0)
#     glutSolidSphere(25, 10, 10)
#     glPopMatrix()
    
#     # Arms and legs based on state
#     if state == BOSS_HEALTHY:
#         # All limbs intact
#         draw_boss_limbs(False, False)
#     elif state == BOSS_WOUNDED:
#         # Limping (visual effect on leg)
#         draw_boss_limbs(True, False)
#     else:  # BOSS_CRITICAL
#         # Missing arm
#         draw_boss_limbs(True, True)
        
#         # Blood effect
#         glColor3f(0.8, 0.0, 0.0)  # Blood red
#         glPushMatrix()
#         glTranslatef(boss_radius + 10, 40, 0)  # Position of detached arm
#         glutSolidSphere(10, 8, 8)  # Blood splatter
#         glPopMatrix()
    
#     # Health bar (red background)
#     glPushMatrix()
#     glTranslatef(0, 120, 0)
#     glRotatef(-angle, 0, 1, 0)  # Counter-rotate to face camera
    
#     glColor3f(1.0, 0.0, 0.0)
#     glBegin(GL_QUADS)
#     glVertex3f(-30, 0, 0)
#     glVertex3f(30, 0, 0)
#     glVertex3f(30, 8, 0)
#     glVertex3f(-30, 8, 0)
#     glEnd()
    
#     # Health bar (green fill)
#     health_pct = max(0, health / boss_max_health)
#     glColor3f(0.0, 1.0, 0.0)
#     glBegin(GL_QUADS)
#     glVertex3f(-30, 0, 0)
#     glVertex3f(-30 + 60 * health_pct, 0, 0)
#     glVertex3f(-30 + 60 * health_pct, 8, 0)
#     glVertex3f(-30, 8, 0)
#     glVertex3f(-30, 0, 0)
#     glVertex3f(-30 + 60 * health_pct, 0, 0)
#     glVertex3f(-30 + 60 * health_pct, 8, 0)
#     glVertex3f(-30, 8, 0)
#     glEnd()
    
#     glPopMatrix()
    
#     glPopMatrix()

"""Helper function to draw boss limbs with visual effects"""
def draw_boss_limbs(limping, missing_arm, missing_leg):
    # LEFT ARM
    if not missing_arm:
        glColor3f(0.7, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(-boss_radius - 8, 50, 0)
        glRotatef(45, 0, 0, 1)
        glScalef(10, 50, 10)
        glutSolidCube(1)
        glPopMatrix()
    
    # RIGHT ARM (always present)
    glColor3f(0.7, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(boss_radius + 8, 50, 0)
    glRotatef(-45, 0, 0, 1)
    glScalef(10, 50, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    # LEFT LEG (always present)
    glColor3f(0.7, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(-boss_radius/2, 0, 0)
    glScalef(15, 40, 15)
    glutSolidCube(1)
    glPopMatrix()
    
    # RIGHT LEG (conditional)
    if not missing_leg:
        glPushMatrix()
        glTranslatef(boss_radius/2, 0, 0)
        
        # Apply limping rotation & color inside the push/pop
        if limping:
            glRotatef(15, 1, 0, 0)
            glColor3f(0.5, 0.0, 0.0)
        else:
            glColor3f(0.7, 0.0, 0.0)
        
        glScalef(15, 40, 15)
        glutSolidCube(1)
        glPopMatrix()


def draw_boss():
    if not boss:
        return

    # Unpack the boss data
    x, z, angle, health, state, _ = boss

    # 1) Position & rotate into world
    glPushMatrix()
    glTranslatef(x, 40, z)         # Lift boss off the ground
    glRotatef(angle, 0, 1, 0)      # Face the player

    # 2. Boss body
    glColor3f(0.8, 0.0, 0.0)  # Red for boss
    glPushMatrix()
    glTranslatef(0, 40, 0)
    glScalef(boss_radius, 80, boss_radius)
    glutSolidCube(1)
    glPopMatrix()
    
    # Boss head
    glColor3f(0.6, 0.0, 0.0)  # Darker red
    glPushMatrix()
    glTranslatef(0, 90, 0)
    glutSolidSphere(25, 10, 10)
    glPopMatrix()
    
    # 3) Decide which limbs to show, based purely on health %:
    health_pct  = health / boss_max_health
    limping     = health_pct < 2/3    # below 66% → limp
    missing_arm = health_pct < 2/3    # below 66% → lose left arm
    missing_leg = health_pct < 1/3    # below 33% → lose right leg

    # 4) Draw arms & legs according to those flags:
    draw_boss_limbs(limping, missing_arm, missing_leg)

    # 5) (Optional) blood splatter when critical
    if health_pct < 1/3:
        glColor3f(0.8, 0, 0)
        glPushMatrix()
        glTranslatef(boss_radius + 10, 40, 0)
        glutSolidSphere(10, 8, 8)
        glPopMatrix()
        
    # 5. Health bar (red background)
    glPushMatrix()
    glTranslatef(0, 120, 0)
    glRotatef(-angle, 0, 1, 0)  # Counter-rotate to face camera
    
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, 0)
    glVertex3f(30, 0, 0)
    glVertex3f(30, 8, 0)
    glVertex3f(-30, 8, 0)
    glEnd()
    
    # Health bar (green fill)
    health_pct = max(0, health / boss_max_health)
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, 0)
    glVertex3f(-30 + 60 * health_pct, 0, 0)
    glVertex3f(-30 + 60 * health_pct, 8, 0)
    glVertex3f(-30, 8, 0)
    glVertex3f(-30, 0, 0)
    glVertex3f(-30 + 60 * health_pct, 0, 0)
    glVertex3f(-30 + 60 * health_pct, 8, 0)
    glVertex3f(-30, 8, 0)
    glEnd()
    
    glPopMatrix()
    
    glPopMatrix()


def draw_projectiles():
    """Draw all projectiles"""
    for x, z, dx, dz, owner in projectiles:
        glPushMatrix()
        
        glTranslatef(x, 30, z)  # All projectiles at player height
        
        if owner == PROJECTILE_PLAYER:
            glColor3f(1.0, 1.0, 0.0)  # Yellow for player bullets
        else:
            glColor3f(1.0, 0.0, 0.0)  # Red for boss projectiles
            
        glutSolidSphere(projectile_radius, 8, 8)
        
        glPopMatrix()

def draw_hud():
    """Draw heads-up display with player info"""
    # Switch to orthographic projection for HUD
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT), 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw health bar background
    glColor3f(0.5, 0.0, 0.0)  # Dark red
    glBegin(GL_QUADS)
    glVertex2f(20, 20)
    glVertex2f(220, 20)
    glVertex2f(220, 40)
    glVertex2f(20, 40)
    glEnd()
    
    # Draw health bar fill
    health_pct = max(0, player_health / 100)
    glColor3f(0.0, 1.0, 0.0)  # Green
    glBegin(GL_QUADS)
    glVertex2f(20, 20)
    glVertex2f(20 + 200 * health_pct, 20)
    glVertex2f(20 + 200 * health_pct, 40)
    glVertex2f(20, 40)
    glEnd()
    
    # Draw ammo indicator background
    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    glBegin(GL_QUADS)
    glVertex2f(20, 50)
    glVertex2f(220, 50)
    glVertex2f(220, 70)
    glVertex2f(20, 70)
    glEnd()
    
    # Draw ammo fill
    ammo_pct = max(0, player_ammo / 30)  # Assuming max ammo is 30
    glColor3f(1.0, 0.7, 0.0)  # Orange/yellow
    glBegin(GL_QUADS)
    glVertex2f(20, 50)
    glVertex2f(20 + 200 * ammo_pct, 50)
    glVertex2f(20 + 200 * ammo_pct, 70)
    glVertex2f(20, 50)
    glEnd()
    
    # Restore projection matrix
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    # Re-enable lighting and depth test
    glEnable(GL_LIGHTING)   
    glEnable(GL_DEPTH_TEST)

def draw_menu():
    """Draw main menu screen"""
    # Switch to orthographic projection for menu
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT), 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    
    # Draw background
    glColor3f(0.1, 0.1, 0.3)  # Dark blue
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(window_width, 0)
    glVertex2f(window_width, window_height)
    glVertex2f(0, window_height)
    glEnd()
    
    # Draw title (would use bitmap text in full implementation)
    # For now, just a placeholder rectangle
    glColor3f(0.8, 0.0, 0.0)  # Red
    glBegin(GL_QUADS)
    glVertex2f(window_width/2 - 200, window_height/4)
    glVertex2f(window_width/2 + 200, window_height/4)
    glVertex2f(window_width/2 + 200, window_height/4 + 80)
    glVertex2f(window_width/2 - 200, window_height/4 + 80)
    glEnd()
    
    # Draw "Press Space to Start" button
    glColor3f(0.0, 0.7, 0.0)  # Green
    glBegin(GL_QUADS)
    glVertex2f(window_width/2 - 150, window_height/2)
    glVertex2f(window_width/2 + 150, window_height/2)
    glVertex2f(window_width/2 + 150, window_height/2 + 60)
    glVertex2f(window_width/2 - 150, window_height/2 + 60)
    glEnd()
    
    # Restore projection matrix
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

def draw_game_over():
    """Draw game over screen"""
    # Switch to orthographic projection
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT), 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    
    # Semi-transparent overlay
    glColor4f(0.0, 0.0, 0.0, 0.7)  # Semi-transparent black
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(window_width, 0)
    glVertex2f(window_width, window_height)
    glVertex2f(0, window_height)
    glEnd()
    
    # Draw "Game Over" text (placeholder rectangle)
    glColor3f(0.8, 0.0, 0.0)  # Red
    glBegin(GL_QUADS)
    glVertex2f(window_width/2 - 150, window_height/3)
    glVertex2f(window_width/2 + 150, window_height/3)
    glVertex2f(window_width/2 + 150, window_height/3 + 60)
    glVertex2f(window_width/2 - 150, window_height/3 + 60)
    glEnd()
    
    # Draw score display (placeholder rectangle)
    glColor3f(1.0, 1.0, 0.0)  # Yellow
    glBegin(GL_QUADS)
    glVertex2f(window_width/2 - 100, window_height/2)
    glVertex2f(window_width/2 + 100, window_height/2)
    glVertex2f(window_width/2 + 100, window_height/2 + 40)
    glVertex2f(window_width/2 - 100, window_height/2 + 40)
    glEnd()
    
    # Draw "Press R to Restart" button
    glColor3f(0.0, 0.7, 0.0)  # Green
    glBegin(GL_QUADS)
    glVertex2f(window_width/2 - 150, window_height*2/3)
    glVertex2f(window_width/2 + 150, window_height*2/3)
    glVertex2f(window_width/2 + 150, window_height*2/3 + 60)
    glVertex2f(window_width/2 - 150, window_height*2/3 + 60)
    glEnd()
    
    # Restore projection matrix
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

def setup_camera():
    """Set up camera view based on current view mode"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, float(glutGet(GLUT_WINDOW_WIDTH))/float(glutGet(GLUT_WINDOW_HEIGHT)), 1, 2000)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if current_view == VIEW_FIRST_PERSON:
        # First person view
        eye_height = player_pos[1] + player_height - 10  # Eye level
        
        # Calculate look direction
        look_x = player_pos[0] + math.sin(math.radians(player_angle)) * 10
        look_z = player_pos[2] - math.cos(math.radians(player_angle)) * 10
        
        gluLookAt(
            player_pos[0], eye_height, player_pos[2],  # Eye position
            look_x, eye_height, look_z,              # Look target
            0, 1, 0                                  # Up vector
        )
    else:
        # Third person view
        # Calculate camera position behind and above player
        distance = 200
        height = 150
        
        cam_x = player_pos[0] - math.sin(math.radians(player_angle)) * distance
        cam_z = player_pos[2] + math.cos(math.radians(player_angle)) * distance
        
        gluLookAt(
            cam_x, player_pos[1] + height, cam_z,  # Camera position
            player_pos[0], player_pos[1] + 50, player_pos[2],  # Look at player
            0, 1, 0                              # Up vector
        )

def display():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if game_state == MENU:
        draw_menu()
    elif game_state == GAME_OVER:
        setup_camera()
        draw_grid()
        draw_walls()
        draw_obstacles()
        draw_zombies()
        if boss:
            draw_boss()
        draw_projectiles()
        draw_player()
        draw_game_over()
    else:  # PLAYING
        setup_camera()
        
        # Draw scene
        draw_grid()
        draw_walls()
        draw_obstacles()
        draw_zombies()
        if boss:
            draw_boss()
        draw_projectiles()
        draw_player()
        
        # Draw HUD on top
        draw_hud()
    
    glutSwapBuffers()

def idle():
    """Idle function for continuous updates"""
    update()
    glutPostRedisplay()

def reshape(width, height):
    """Window reshape function"""
    glViewport(0, 0, width, height)
    glutPostRedisplay()

# Movement flags for smooth motion
move_forward = False
move_backward = False
turn_left = False
turn_right = False
strafe_left = False
strafe_right = False

def keyboard(key, x, y):
    """Handle regular key presses"""
    global game_state, current_view, move_forward, move_backward, turn_left, turn_right, strafe_left, strafe_right
    
    if key == b' ':  # Space
        if game_state == MENU:
            init_game()  # Start game
        elif game_state == PLAYING:
            shoot_projectile(PROJECTILE_PLAYER)  # Fire weapon
    
    elif key == b'r' or key == b'R':
        if game_state == GAME_OVER:
            init_game()  # Restart game
    
    elif key == b'v' or key == b'V':
        # Toggle camera view
        current_view = 1 - current_view  # Toggle between 0 and 1
    
    # Movement controls (set flags)
    elif key == b'w' or key == b'W':
        move_forward = True
    elif key == b's' or key == b'S':
        move_backward = True
    elif key == b'a' or key == b'A':
        strafe_left = True
    elif key == b'd' or key == b'D':
        strafe_right = True
    elif key == b'q' or key == b'Q':
        turn_left = True
    elif key == b'e' or key == b'E':
        turn_right = True
    
    # ESC key
    elif key == b'\x1b':
        if game_state == PLAYING:
            game_state = MENU
        else:
            sys.exit(0)

def keyboard_up(key, x, y):
    """Handle key releases for smooth movement"""
    global move_forward, move_backward, turn_left, turn_right, strafe_left, strafe_right
    
    # Clear movement flags on key release
    if key == b'w' or key == b'W':
        move_forward = False
    elif key == b's' or key == b'S':
        move_backward = False
    elif key == b'a' or key == b'A':
        strafe_left = False
    elif key == b'd' or key == b'D':
        strafe_right = False
    elif key == b'q' or key == b'Q':
        turn_left = False
    elif key == b'e' or key == b'E':
        turn_right = False

def special_keys(key, x, y):
    """Handle special key presses (arrow keys)"""
    global move_forward, move_backward, turn_left, turn_right
    
    if key == GLUT_KEY_UP:
        move_forward = True
    elif key == GLUT_KEY_DOWN:
        move_backward = True
    elif key == GLUT_KEY_LEFT:
        turn_left = True
    elif key == GLUT_KEY_RIGHT:
        turn_right = True

def special_keys_up(key, x, y):
    """Handle special key releases"""
    global move_forward, move_backward, turn_left, turn_right
    
    if key == GLUT_KEY_UP:
        move_forward = False
    elif key == GLUT_KEY_DOWN:
        move_backward = False
    elif key == GLUT_KEY_LEFT:
        turn_left = False
    elif key == GLUT_KEY_RIGHT:
        turn_right = False

def mouse(button, state, x, y):
    """Handle mouse clicks"""
    if game_state == PLAYING and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        shoot_projectile(PROJECTILE_PLAYER)

def motion(x, y):
    """Handle mouse movement for looking around"""
    if game_state != PLAYING:
        return
        
    # Implementation would depend on whether we want mouse look
    # For simplicity in this example, we're not implementing full mouse look

def handle_movement():
    """Process movement based on current input flags"""
    global player_pos, player_angle
    
    # Only process movement in PLAYING state
    if game_state != PLAYING:
        return
        
    # Store old position
    old_x, old_y, old_z = player_pos
    
    # Calculate movement vector based on player orientation
    forward_x = math.sin(math.radians(player_angle))
    forward_z = -math.cos(math.radians(player_angle))
    
    # Calculate strafe vector (perpendicular to forward)
    strafe_x = math.sin(math.radians(player_angle + 90))
    strafe_z = -math.cos(math.radians(player_angle + 90))
    
    # Apply movement based on active flags
    if move_forward:
        player_pos[0] += forward_x * player_speed
        player_pos[2] += forward_z * player_speed
    
    if move_backward:
        player_pos[0] -= forward_x * player_speed
        player_pos[2] -= forward_z * player_speed
    
    if strafe_left:
        player_pos[0] -= strafe_x * player_speed
        player_pos[2] -= strafe_z * player_speed
    
    if strafe_right:
        player_pos[0] += strafe_x * player_speed
        player_pos[2] += strafe_z * player_speed
    
    # Apply rotation
    if turn_left:
        player_angle -= 2
    if turn_right:
        player_angle += 2
    
    # Normalize angle to 0-360
    player_angle %= 360
    
    # Check boundaries
    if (player_pos[0] < -field_size/2 + player_radius or 
        player_pos[0] > field_size/2 - player_radius or
        player_pos[2] < -field_size/2 + player_radius or 
        player_pos[2] > field_size/2 - player_radius):
        # Revert position if out of bounds
        player_pos[0], player_pos[2] = old_x, old_z
        
    # Check obstacle collisions
    for ox, oz, otype, oradius in obstacles:
        dx = player_pos[0] - ox
        dz = player_pos[2] - oz
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance < player_radius + oradius:
            # Collision detected, revert position
            player_pos[0], player_pos[2] = old_x, old_z
            break

def update_player():
    """Update player state"""
    # Handle player movement based on input flags
    handle_movement()
    global player_health
    # Check if player is dead
    if player_health <= 0:
        player_health = 0
        game_state = GAME_OVER

def init():
    """Initialize OpenGL settings"""
    # glClearColor(0.5, 0.7, 1.0, 0.0)  # Sky blue background
    glClearColor(0.05, 0.05, 0.05, 1.0)  # Dark background
    glEnable(GL_DEPTH_TEST)
    
    # Enable lighting for better 3D appearance
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Set up light 0
    light_position = [0, 300, 0, 1]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    # Enable color material for easier coloring
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

def main():
    """Main function to initialize and start the game"""
    global last_time
    
    # Initialize GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Zombie Shooter 3D")
    
    # Register callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutSpecialUpFunc(special_keys_up)
    glutMouseFunc(mouse)
    glutPassiveMotionFunc(motion)
    glutIdleFunc(idle)
    
    # Initialize OpenGL
    init()
    init_game()  # Initialize game state
     
    # Initialize game elements
    generate_obstacles()
    
    # Start time tracking
    last_time = glutGet(GLUT_ELAPSED_TIME)
    
    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    main()