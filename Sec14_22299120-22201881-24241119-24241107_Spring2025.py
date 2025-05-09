from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys


# Lighting and day/night variables
is_night = False
day_ambient = [0.5, 0.5, 0.5, 1.0]
night_ambient = [0.1, 0.1, 0.2, 1.0]  # Dark blue-ish ambient at night
current_ambient = day_ambient
light_transition_speed = 0.01
# Health pickups
health_pickups = []  # Will store (x, z, amount, time_created)
HEALTH_PICKUP_RADIUS = 10
HEALTH_PICKUP_AMOUNT = 20
HEALTH_PICKUP_LIFETIME = 5000  # milliseconds (5 seconds)

# Ammo pickups
ammo_pickups = []  # Will store (x, z, amount, time_created)
AMMO_PICKUP_RADIUS = 10
AMMO_PICKUP_AMOUNT = 10
AMMO_PICKUP_LIFETIME = 5000  # milliseconds (5 seconds)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Level tracking
current_level = 1
zombies_to_kill_for_boss = 15  # Number of zombies to kill before boss appears

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

def spawn_health_pickup(x, z):
    health_pickups.append([x, z, HEALTH_PICKUP_AMOUNT, glutGet(GLUT_ELAPSED_TIME)])


#===========================================================================================
def update_health_pickups():
    global health_pickups, player_health
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    pickups_to_remove = []
    
    for i, pickup in enumerate(health_pickups):
        x, z, amount, spawn_time = pickup
        
        # Check if pickup has expired
        if current_time - spawn_time > HEALTH_PICKUP_LIFETIME:
            pickups_to_remove.append(i)
            continue
            
        # Check if player collected the pickup
        distance = math.sqrt((x - player_pos[0])**2 + (z - player_pos[2])**2)
        if distance < player_radius + HEALTH_PICKUP_RADIUS:
            player_health = min(100, player_health + amount)  # Cap health at 100
            pickups_to_remove.append(i)
    
    # Remove collected/expired pickups
    for i in sorted(pickups_to_remove, reverse=True):
        health_pickups.pop(i)
#=============================================================================================================
def spawn_ammo_pickup(x, z):
    ammo_pickups.append([x, z, AMMO_PICKUP_AMOUNT, glutGet(GLUT_ELAPSED_TIME)])

def update_ammo_pickups():
    global ammo_pickups, player_ammo
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    pickups_to_remove = []
    
    for i, pickup in enumerate(ammo_pickups):
        x, z, amount, spawn_time = pickup
        
        # Check if pickup has expired
        if current_time - spawn_time > AMMO_PICKUP_LIFETIME:
            pickups_to_remove.append(i)
            continue
            
        # Check if player collected the pickup
        distance = math.sqrt((x - player_pos[0])**2 + (z - player_pos[2])**2)
        if distance < player_radius + AMMO_PICKUP_RADIUS:
            player_ammo += amount
            pickups_to_remove.append(i)
    
    # Remove collected/expired pickups
    for i in sorted(pickups_to_remove, reverse=True):
        ammo_pickups.pop(i)

def draw_ammo_pickups():
    for x, z, amount, spawn_time in ammo_pickups:
        glPushMatrix()
        glTranslatef(x, AMMO_PICKUP_RADIUS, z)  # Position slightly above ground
        glColor3f(0.0, 0.0, 1.0)  # Blue color
        glutSolidSphere(AMMO_PICKUP_RADIUS, 10, 10)
        glPopMatrix()
#=============================================================================================================


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
zombies = []  # Will store (x, z, angle, health, state, is_boss) for each zombie
zombie_radius = 15
zombie_speed = 1
zombie_damage = 10
zombie_health = 50
zombie_spawn_timer = 0
zombie_spawn_interval = 3000  # milliseconds
zombie_kill_count = 0
wave_zombie_limit = 5

# Boss zombie variables
boss_zombie_health = 200
boss_zombie_radius = 30
boss_zombie_damage = 20
boss_zombie_speed = 1
boss_exists = False

NORMAL_ZOMBIE_DAMAGE = zombie_health

# Boss variables
boss = None  # Will be (x, z, angle, health, state, projectile_timer) when spawned
boss_radius = 40
boss_speed = 0.5
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

# Movement flags for smooth motion
move_forward = False
move_backward = False
turn_left = False
turn_right = False
strafe_left = False
strafe_right = False

def init_game():
    """Initialize or reset the game to starting state"""
    global player_pos, player_angle, player_health, player_ammo, player_score
    global zombies, boss, obstacles, projectiles, zombie_kill_count, missed_shots
    global game_state, boss_exists, current_level, health_pickups, is_night, current_ambient
    
    # Reset to daytime
    is_night = False
    current_ambient = day_ambient.copy()
    glLightfv(GL_LIGHT0, GL_AMBIENT, current_ambient)

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
    boss_exists = False
    projectiles = []
    zombie_kill_count = 0
    current_level = 1
    health_pickups = []
    
    # Generate obstacles
    generate_obstacles()
    
    # Set game state to playing
    game_state = PLAYING

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def update_lighting():
    """Transition between day and night lighting"""
    global current_ambient, is_night
    
    target_ambient = night_ambient if is_night else day_ambient
    transition_speed = light_transition_speed * (2 if not is_night else 1)  # Faster transition to day
    
    # Smoothly transition ambient light
    for i in range(3):
        if current_ambient[i] < target_ambient[i]:
            current_ambient[i] = min(current_ambient[i] + transition_speed, target_ambient[i])
        elif current_ambient[i] > target_ambient[i]:
            current_ambient[i] = max(current_ambient[i] - transition_speed, target_ambient[i])
    
    # Update the lighting
    glLightfv(GL_LIGHT0, GL_AMBIENT, current_ambient)
#==============================================================

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
                if math.sqrt((x-ox)**2 + (z-oz)**2) < oradius + 35:  # 35 = rock radius + spacing
                    overlap = True
                    break
                    
            if not overlap:
                obstacles.append((x, z, OBSTACLE_ROCK, 20))  # Rocks have radius 20
                break

def spawn_zombie(is_boss=False):
    """Spawn a zombie at a random position outside player safe radius"""
    global is_night, boss_exists
    
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
    
    if is_boss:
        zombies.append([x, z, 0, boss_zombie_health, 0, True])
        boss_exists = True
        is_night = True  # Turn to night when boss spawns
    else:
        zombies.append([x, z, 0, zombie_health, 0, False])

def spawn_boss():
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
#=============================================================================
def draw_health_pickups():
    for x, z, amount, spawn_time in health_pickups:
        glPushMatrix()
        glTranslatef(x, HEALTH_PICKUP_RADIUS, z)  # Position slightly above ground
        glColor3f(0.0, 1.0, 0.0)  # Green color
        glutSolidSphere(HEALTH_PICKUP_RADIUS, 10, 10)
        glPopMatrix()
#==============================================================================

def shoot_projectile(owner_type):
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

def handle_movement():
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

def update_zombies():
    global zombies, player_health, zombie_kill_count, player_score, boss_exists, current_level
    
    zombies_to_remove = []
    current_time = glutGet(GLUT_ELAPSED_TIME)
    
    for i, zombie in enumerate(zombies):
        x, z, angle, health, state, is_boss = zombie
        
        # Calculate direction to player
        dx = player_pos[0] - x
        dz = player_pos[2] - z
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dz /= distance
            
            # Update zombie angle to face player
            new_angle = math.degrees(math.atan2(dx, -dz)) % 360
            zombies[i][2] = new_angle
            
            # Move toward player if not too close
            if distance > (player_radius + zombie_radius + 5):
                new_x = x + dx * zombie_speed
                new_z = z + dz * zombie_speed
                
                # Check collisions before moving
                if not check_collision(new_x, new_z, zombie_radius):
                    zombies[i][0] = new_x
                    zombies[i][1] = new_z
            else:
                # Close enough to attack - deal damage
                if current_time % 1000 < time_delta:  # Damage every second
                    player_health -= zombie_damage
        
        # Check if zombie is dead
        if health <= 0:
            zombies_to_remove.append(i)
            zombie_kill_count += 1
            player_score += 300 if is_boss else 100
            
            # Random chance to drop pickups (30% health, 30% ammo)
            if random.random() < 0.3:
                spawn_health_pickup(x, z)
            if random.random() < 0.3:
                spawn_ammo_pickup(x, z)
            
            if is_boss:
                boss_exists = False
                current_level += 1  # Level up after killing a boss
    
    # Remove dead zombies (in reverse order to avoid index shifting)
    for i in sorted(zombies_to_remove, reverse=True):
        zombies.pop(i)

def update_boss():
    global boss, player_health, is_night, boss_exists
    
    if not boss:
        return
        
    x, z, angle, health, state, projectile_timer = boss

    # If boss is dead, return to daytime
    if health <= 0:
        is_night = False
    
     # Update boss state based on health
    if health <= 0:
        boss_exists = False
        is_night = False  # Return to daytime when boss dies
        return
    
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
    
        # Rest of the boss update logic remains the same...
    if health <= boss_max_health / 3 and state != BOSS_CRITICAL:
        boss[4] = BOSS_CRITICAL
    elif health <= boss_max_health * 2/3 and state != BOSS_WOUNDED and state != BOSS_CRITICAL:
        boss[4] = BOSS_WOUNDED

def update_projectiles():
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
    global game_state, zombie_kill_count, boss, zombie_spawn_timer, boss_exists, current_level
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    
    if game_state == PLAYING:
        # Check for game over condition
        if player_health <= 0:
            game_state = GAME_OVER
            return
            
        # Check if we should spawn boss based on zombie kill count
        if zombie_kill_count >= zombies_to_kill_for_boss and not boss_exists:
            spawn_zombie(is_boss=True)
            zombie_kill_count = 0  # Reset kill count
            
        # Spawn regular zombies if not at max and no boss is active
        if len(zombies) < wave_zombie_limit:
            if current_time - zombie_spawn_timer > zombie_spawn_interval:
                spawn_zombie(is_boss=False)
                zombie_spawn_timer = current_time

def update():
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
        update_health_pickups()
        update_ammo_pickups()
        update_game_state()
        update_lighting()  # Add this line
    
    glutPostRedisplay()
def draw_grid():
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
    for x, z, angle, health, state, is_boss in zombies:
        glPushMatrix()
        
        glTranslatef(x, 30, z)
        glRotatef(angle, 0, 1, 0)
        
        if is_boss:
            glScalef(2.0, 2.0, 2.0)
            radius = boss_zombie_radius
            max_health = boss_zombie_health
            body_color = (0.6, 0.4, 0.35)  # Pale flesh tone
            head_color = (0.6, 0.38, 0.3)  # Slightly different for head
            limb_color = (0.58, 0.36, 0.28)
        else:
            radius = zombie_radius
            max_health = zombie_health
            # Regular zombie color is green
            body_color = (0.0, 0.8, 0.0)  # Green for zombies
            head_color = (0.0, 0.6, 0.0)  # Darker green
            limb_color = (0.0, 0.7, 0.0)
        
        # Zombie body
        glColor3f(*body_color)
        glPushMatrix()
        glTranslatef(0, 20, 0)
        
        if is_boss:
            # Torso
            glPushMatrix()
            glScalef(radius*0.7, 35, radius*0.5)
            glutSolidCube(1)
            glPopMatrix()
            
            # Chest blood and wounds
            glColor3f(0.7, 0.0, 0.0)  # Dark red for blood
            
            # Main chest wound
            glPushMatrix()
            glTranslatef(0, 10, radius*0.5 + 0.5)
            glRotatef(90, 1, 0, 0)
            gluDisk(gluNewQuadric(), 0, 8, 12, 1)
            glPopMatrix()
            
            # Blood stains on chest
            glPushMatrix()
            glTranslatef(-radius*0.3, 5, radius*0.5 + 0.2)
            glRotatef(90, 1, 0, 0)
            gluDisk(gluNewQuadric(), 0, 4, 8, 1)
            glPopMatrix()
            
            glPushMatrix()
            glTranslatef(radius*0.25, 0, radius*0.5 + 0.2)
            glRotatef(90, 1, 0, 0)
            gluDisk(gluNewQuadric(), 0, 5, 8, 1)
            glPopMatrix()
            
            # Blood drips
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 5, radius*0.5 + 0.5)
            glVertex3f(-3, -10, radius*0.5 + 0.5)
            glVertex3f(3, -10, radius*0.5 + 0.5)
            glEnd()
            
            # Restore body color
            glColor3f(*body_color)
        else:
            # Regular zombie body
            glScalef(radius, 50, radius)
            glutSolidCube(1)
        
        glPopMatrix()
        
        # Zombie head
        glColor3f(*head_color)
        glPushMatrix()
        glTranslatef(0, 55, 0)
        
        if is_boss:
            # More detailed head for boss
            # Base head sphere
            glutSolidSphere(15, 16, 16)
            
            # Jaw/mouth area
            glPushMatrix()
            glTranslatef(0, -5, 5)
            glScalef(12, 5, 10)
            glutSolidCube(1)
            glPopMatrix()
            
            # Bloody mouth
            glColor3f(0.7, 0.0, 0.0)  # Blood red
            glPushMatrix()
            glTranslatef(0, -5, 10)
            glRotatef(90, 1, 0, 0)
            gluDisk(gluNewQuadric(), 0, 6, 12, 1)  # Blood pool in mouth
            glPopMatrix()
            
            # Blood dripping from mouth
            glBegin(GL_TRIANGLES)
            glVertex3f(0, -5, 10)
            glVertex3f(-4, -15, 8)
            glVertex3f(4, -15, 8)
            glEnd()
            
            # Bloody eyes
            glPushMatrix()
            glTranslatef(-5, 0, 10)
            glutSolidSphere(3, 8, 8)
            glPopMatrix()
            
            glPushMatrix()
            glTranslatef(5, 0, 10)
            glutSolidSphere(3, 8, 8)
            glPopMatrix()
            
            # Facial features - nose
            glColor3f(*head_color)
            glPushMatrix()
            glTranslatef(0, -2, 12)
            glRotatef(-90, 1, 0, 0)
            glutSolidCone(3, 5, 8, 8)
            glPopMatrix()
            
            # Ears
            glPushMatrix()
            glTranslatef(-13, 0, 0)
            glRotatef(90, 0, 1, 0)
            glScalef(1, 2, 0.5)
            glutSolidCone(3, 5, 8, 4)
            glPopMatrix()
            
            glPushMatrix()
            glTranslatef(13, 0, 0)
            glRotatef(-90, 0, 1, 0)
            glScalef(1, 2, 0.5)
            glutSolidCone(3, 5, 8, 4)
            glPopMatrix()
            
            # Restore head color
            glColor3f(*head_color)
        else:
            # Regular zombie head
            glutSolidSphere(15, 10, 10)
        
        glPopMatrix()
        
        # Arms
        glColor3f(*limb_color)
        
        if is_boss:
            # More detailed arms for boss
            
            # Left arm - upper arm
            glPushMatrix()
            glTranslatef(-radius - 5, 30, 0)
            glRotatef(20, 0, 0, 1)
            glRotatef(-10, 1, 0, 0)
            
            # Upper arm
            glPushMatrix()
            glScalef(8, 25, 8)
            glutSolidCube(1)
            glPopMatrix()
            
            # Left forearm
            glTranslatef(0, -20, 5)
            glRotatef(20, 1, 0, 0)
            
            glPushMatrix()
            glScalef(7, 22, 7)
            glutSolidCube(1)
            glPopMatrix()
            
            # Left hand
            glTranslatef(0, -15, 0)
            
            glPushMatrix()
            glutSolidSphere(5, 8, 8)
            
            # Fingers
            for i in range(5):
                glPushMatrix()
                angle = -30 + i * 15
                glRotatef(angle, 0, 1, 0)
                glTranslatef(0, -5, 0)
                glScalef(1.5, 7, 1.5)
                glutSolidCube(1)
                glPopMatrix()
            
            glPopMatrix()
            glPopMatrix()
            
            # Right arm - upper arm
            glPushMatrix()
            glTranslatef(radius + 5, 30, 0)
            glRotatef(-20, 0, 0, 1)
            glRotatef(-10, 1, 0, 0)
            
            # Upper arm
            glPushMatrix()
            glScalef(8, 25, 8)
            glutSolidCube(1)
            glPopMatrix()
            
            # Right forearm
            glTranslatef(0, -20, 5)
            glRotatef(20, 1, 0, 0)
            
            glPushMatrix()
            glScalef(7, 22, 7)
            glutSolidCube(1)
            glPopMatrix()
            
            # Right hand with blood
            glTranslatef(0, -15, 0)
            
            glPushMatrix()
            glutSolidSphere(5, 8, 8)
            
            # Bloody hand
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(0, -3, 3)
            glutSolidSphere(4, 8, 8)
            glPopMatrix()
            
            # Restore limb color for fingers
            glColor3f(*limb_color)
            
            # Fingers
            for i in range(5):
                glPushMatrix()
                angle = -30 + i * 15
                glRotatef(angle, 0, 1, 0)
                glTranslatef(0, -5, 0)
                glScalef(1.5, 7, 1.5)
                glutSolidCube(1)
                glPopMatrix()
            
            glPopMatrix()
            glPopMatrix()
            
            # Legs for boss
            # Left leg
            glPushMatrix()
            glTranslatef(-radius*0.4, -30, 0)
            
            # Upper leg
            glPushMatrix()
            glScalef(radius*0.5, 30, radius*0.5)
            glutSolidCube(1)
            glPopMatrix()
            
            # Lower leg
            glTranslatef(0, -30, 0)
            glRotatef(10, 1, 0, 0)
            
            glPushMatrix()
            glScalef(radius*0.45, 30, radius*0.45)
            glutSolidCube(1)
            glPopMatrix()
            
            # Foot
            glTranslatef(0, -18, 5)
            glScalef(radius*0.5, 6, radius*0.8)
            glutSolidCube(1)
            glPopMatrix()
            
            # Right leg
            glPushMatrix()
            glTranslatef(radius*0.4, -30, 0)
            
            # Upper leg
            glPushMatrix()
            glScalef(radius*0.5, 30, radius*0.5)
            glutSolidCube(1)
            glPopMatrix()
            
            # Lower leg
            glTranslatef(0, -30, 0)
            glRotatef(10, 1, 0, 0)
            
            glPushMatrix()
            glScalef(radius*0.45, 30, radius*0.45)
            glutSolidCube(1)
            glPopMatrix()
            
            # Foot
            glTranslatef(0, -18, 5)
            glScalef(radius*0.5, 6, radius*0.8)
            glutSolidCube(1)
            glPopMatrix()
        else:
            # Left arm for regular zombie
            glPushMatrix()
            glTranslatef(-radius - 5, 30, 0)
            glRotatef(45, 0, 0, 1)
            glScalef(5, 30, 5)
            glutSolidCube(1)
            glPopMatrix()
            
            # Right arm for regular zombie
            glPushMatrix()
            glTranslatef(radius + 5, 30, 0)
            glRotatef(-45, 0, 0, 1)
            glScalef(5, 30, 5)
            glutSolidCube(1)
            glPopMatrix()
        
        # Health bar dimensions depend on zombie type
        bar_width = 40 if is_boss else 15
        bar_height = 8 if is_boss else 5
        bar_y_offset = 100 if is_boss else 70
        
        # Health bar (red background)
        glPushMatrix()
        glTranslatef(0, bar_y_offset, 0)
        glRotatef(-angle, 0, 1, 0)  # Counter-rotate to face camera
        
        glColor3f(1.0, 0.0, 0.0)  # Red background
        glBegin(GL_QUADS)
        glVertex3f(-bar_width, 0, 0)
        glVertex3f(bar_width, 0, 0)
        glVertex3f(bar_width, bar_height, 0)
        glVertex3f(-bar_width, bar_height, 0)
        glEnd()
        
        # Health bar (green fill)
        health_pct = max(0, health / max_health)
        glColor3f(0.0, 1.0, 0.0)  # Green fill
        glBegin(GL_QUADS)
        glVertex3f(-bar_width, 0, 0)
        glVertex3f(-bar_width + 2 * bar_width * health_pct, 0, 0)
        glVertex3f(-bar_width + 2 * bar_width * health_pct, bar_height, 0)
        glVertex3f(-bar_width, bar_height, 0)
        glEnd()
        
        glPopMatrix()
        
        glPopMatrix()

def draw_projectiles():
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
    
    # Draw level indicator
    glColor3f(0.1, 0.1, 0.6)  # Dark blue
    glBegin(GL_QUADS)
    glVertex2f(20, 80)
    glVertex2f(220, 80)
    glVertex2f(220, 100)
    glVertex2f(20, 100)
    glEnd()
    
    # Add level text (simulate with a different color block)
    glColor3f(0.3, 0.3, 1.0)  # Lighter blue
    glBegin(GL_QUADS)
    glVertex2f(20, 80)
    glVertex2f(20 + (current_level * 40), 80)  # Width based on level
    glVertex2f(20 + (current_level * 40), 100)
    glVertex2f(20, 100)
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
    
    # Set text color to white
    glColor3f(1.0, 1.0, 1.0)
    
    # Draw "Game Over" text
    glRasterPos2f(window_width/2 - 50, window_height/3)
    text = "GAME OVER"
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    
    # Draw score text
    glRasterPos2f(window_width/2 - 70, window_height/2 - 20)
    score_text = f"SCORE: {player_score}"
    for character in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    
    # Draw "Press R to Restart" text
    glRasterPos2f(window_width/2 - 80, window_height*2/3 + 20)
    restart_text = "Press R to Restart"
    for character in restart_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))
    
    # Draw a decorative border around the game over screen
    glColor3f(0.8, 0.0, 0.0)  # Red border
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(window_width/2 - 200, window_height/3 - 50)
    glVertex2f(window_width/2 + 200, window_height/3 - 50)
    glVertex2f(window_width/2 + 200, window_height*2/3 + 50)
    glVertex2f(window_width/2 - 200, window_height*2/3 + 50)
    glEnd()
    glLineWidth(1.0)
    
    # Restore projection matrix
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

def setup_camera():
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
        draw_health_pickups()
        draw_ammo_pickups()  # Add this line
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
        draw_health_pickups()
        draw_ammo_pickups()  # Add this line
        draw_player()
        
        # Draw HUD on top
        draw_hud()
    
    glutSwapBuffers()

def idle():
    update()
    glutPostRedisplay()

def reshape(width, height):
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
    
    # # ESC key
    # elif key == b'\x1b':
    #     if game_state == PLAYING:
    #         game_state = MENU
    #     else:
    #         sys.exit(0)

def keyboard_up(key, x, y):
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
    if game_state == PLAYING and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        shoot_projectile(PROJECTILE_PLAYER)

def motion(x, y):
    if game_state != PLAYING:
        return
        
    # Implementation would depend on whether we want mouse look
    # For simplicity in this example, we're not implementing full mouse look


def update_player():
    # Handle player movement based on input flags
    handle_movement()
    global player_health
    # Check if player is dead
    if player_health <= 0:
        player_health = 0
        game_state = GAME_OVER

def init():
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

    
    #==========================================================================================
class WeaponPickup:
    def __init__(self, x, z, weapon_type):
        self.x = x
        self.z = z
        self.weapon_type = weapon_type
        self.radius = 15
        self.time_created = glutGet(GLUT_ELAPSED_TIME)
        self.lifetime = 10000  # 10 seconds


def check_weapon_pickups():
    global weapon_pickups, player_weapon
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    pickups_to_remove = []
    
    for i, pickup in enumerate(weapon_pickups):
        # Check if expired
        if current_time - pickup.time_created > pickup.lifetime:
            pickups_to_remove.append(i)
            continue
            
        # Check collision with player
        distance = math.sqrt((pickup.x - player_pos[0])**2 + (pickup.z - player_pos[2])**2)
        if distance < player_radius + pickup.radius:
            player_weapon.type = pickup.weapon_type
            pickups_to_remove.append(i)
    
    # Remove collected/expired pickups
    for i in sorted(pickups_to_remove, reverse=True):
        weapon_pickups.pop(i)
#==============================================================================================
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
                if math.sqrt((x-ox)**2 + (z-oz)**2) < oradius + 35:  # 35 = rock radius + spacing
                    overlap = True
                    break
                    
            if not overlap:
                obstacles.append((x, z, OBSTACLE_ROCK, 20))  # Rocks have radius 20
                break


#==========================================================================
class Weapon:
    def __init__(self):
        self.type = "pistol"  # Start with pistol
        self.damage = 20
        self.ammo = 15
        self.max_ammo = 15
        self.fire_rate = 500  # ms between shots
        self.last_shot = 0
        self.upgrades = []
        self.model_details = self._get_model_details()

    def _get_model_details(self):
        if self.type == "pistol":
            return {
                "main_color": (0.3, 0.3, 0.3),
                "secondary_color": (0.5, 0.5, 0.5),
                "barrel_length": 20,
                "body_width": 4,
                "grip_color": (0.15, 0.15, 0.15),
                "has_sight": False
            }
        elif self.type == "rifle":
            return {
                "main_color": (0.2, 0.2, 0.2),
                "secondary_color": (0.4, 0.4, 0.4),
                "barrel_length": 30,
                "body_width": 5,
                "grip_color": (0.4, 0.3, 0.2),  # Wooden
                "has_sight": True,
                "stock_length": 10
            }
        elif self.type == "shotgun":
            return {
                "main_color": (0.4, 0.3, 0.2),
                "secondary_color": (0.3, 0.3, 0.3),
                "barrel_length": 25,
                "body_width": 6,
                "grip_color": (0.15, 0.15, 0.15),
                "has_sight": False,
                "pump_offset": 5
            }

    def draw(self, x, y, z, angle, recently_fired):
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(angle, 0, 1, 0)
        glRotatef(-10, 1, 0, 0)  # Tilt gun downward slightly
        
        if self.type == "pistol":
            self._draw_pistol(recently_fired)
        elif self.type == "rifle":
            self._draw_rifle(recently_fired)
        elif self.type == "shotgun":
            self._draw_shotgun(recently_fired)
        
        glPopMatrix()

    def _draw_pistol(self, recently_fired):
        """Detailed pistol model"""
        details = self.model_details
        
        # Main body
        glColor3f(*details["main_color"])
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        glScalef(details["body_width"], 3, details["barrel_length"])
        glutSolidCube(1)
        glPopMatrix()
        
        # Grip
        glColor3f(*details["grip_color"])
        glPushMatrix()
        glTranslatef(-3, -5, -5)
        glRotatef(90, 0, 1, 0)
        glScalef(3, 8, 4)
        glutSolidCube(1)
        glPopMatrix()
        
        # Trigger
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(-1, -2, -3)
        glScalef(1.5, 0.5, 1)
        glutSolidCube(1)
        glPopMatrix()
        
        # Muzzle flash
        if recently_fired:
            glColor3f(1.0, 0.7, 0.0)
            glPushMatrix()
            glRotatef(90, 0, 1, 0)
            glTranslatef(0, 0, details["barrel_length"]/2)
            glutSolidSphere(3, 8, 8)
            glPopMatrix()

    def _draw_rifle(self, recently_fired):
        """Detailed rifle model"""
        details = self.model_details
        
        # Main barrel
        glColor3f(*details["main_color"])
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        glScalef(details["body_width"], 4, details["barrel_length"])
        glutSolidCube(1)
        glPopMatrix()
        
        # Stock
        glColor3f(*details["grip_color"])
        glPushMatrix()
        glTranslatef(-6, 0, -details["stock_length"]/2)
        glRotatef(90, 0, 1, 0)
        glScalef(6, 4, details["stock_length"])
        glutSolidCube(1)
        glPopMatrix()
        
        # Magazine
        glColor3f(*details["secondary_color"])
        glPushMatrix()
        glTranslatef(-3, -3, 0)
        glRotatef(90, 0, 1, 0)
        glScalef(4, 6, 6)
        glutSolidCube(1)
        glPopMatrix()
        
        # Scope
        if details["has_sight"]:
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(6, 3, 5)
            glRotatef(90, 0, 1, 0)
            glutSolidCylinder(1.5, 10, 10, 2)
            
            # Lens
            glColor3f(0.0, 0.5, 0.8)
            glTranslatef(0, 0, 10)
            glutSolidSphere(1.5, 10, 10)
            glPopMatrix()
        
        # Muzzle flash
        if recently_fired:
            glColor3f(1.0, 0.5, 0.0)
            glPushMatrix()
            glRotatef(90, 0, 1, 0)
            glTranslatef(0, 0, details["barrel_length"]/2)
            glutSolidSphere(4, 8, 8)
            glPopMatrix()


    def switch_weapon(self, weapon_type):
        """Change to a different weapon"""
        self.type = weapon_type
        self.model_details = self._get_model_details()
        
        # Update stats based on new weapon
        if weapon_type == "pistol":
            self.damage = 20
            self.max_ammo = 15
        elif weapon_type == "rifle":
            self.damage = 30
            self.max_ammo = 30
        elif weapon_type == "shotgun":
            self.damage = 40
            self.max_ammo = 8
        
        self.ammo = self.max_ammo  # Refill ammo when switching

    def add_visual_upgrade(self, upgrade_type):
        if upgrade_type == "sight":
            self.model_details["has_sight"] = True
        elif upgrade_type == "extended_mag":
            self.model_details["body_width"] += 1  # Make magazine visually larger
        elif upgrade_type == "gold":
            self.model_details["main_color"] = (0.8, 0.7, 0.1)  # Gold tint
#=====================================================================================


if __name__ == "__main__":
    main()