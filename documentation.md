
---

# **Zombie Shooter 3D Game - Documentation**

This script implements a 3D zombie shooting game using **OpenGL** and **GLUT** for graphics and window management. The game involves a player character who must survive waves of zombies, including a powerful boss zombie. The player can shoot projectiles and interact with obstacles in a 3D environment.

## **Overview**

The game is structured around different states and entities:

* **Game States:**

  * `MENU`: The main menu where the player can start or quit the game.
  * `PLAYING`: The active state where the game is ongoing.
  * `GAME_OVER`: The state when the player’s health reaches zero.

* **Entities:**

  * **Player**: The main character controlled by the user.
  * **Zombies**: Enemies that spawn and move towards the player.
  * **Boss Zombie**: A special zombie with higher health and stronger attacks.
  * **Projectiles**: Bullets fired by the player and the boss.

---

## **Key Variables**

### **Game States**

* `MENU`: The state for the main menu.
* `PLAYING`: The state when the game is in progress.
* `GAME_OVER`: The state when the game ends.

### **Camera Variables**

* `camera_pos`: Position of the camera in 3D space.
* `fovY`: Field of view in the vertical direction.
* `GRID_LENGTH`: The length of the field grid.
* `VIEW_FIRST_PERSON`: Flag for first-person view.
* `VIEW_THIRD_PERSON`: Flag for third-person view.
* `current_view`: The current view mode (either first or third person).

### **Player Variables**

* `player_pos`: The player’s position in the game world (x, y, z).
* `player_angle`: The direction the player is facing, in degrees.
* `player_health`: The player’s health.
* `player_ammo`: The amount of ammunition the player has.
* `player_score`: The player’s current score.
* `player_radius`: The radius of the player's character for collision detection.
* `player_height`: The height of the player.
* `player_speed`: The speed at which the player moves.
* `missed_shots`: Counter for missed shots.
* `last_shot_time`: The time when the player last fired a shot.
* `shot_cooldown`: Time in milliseconds between two consecutive shots.

### **Field and Boundary Variables**

* `field_size`: The size of the game field (grid).
* `wall_height`: The height of the boundary walls.

### **Obstacle Variables**

* `num_trees`: The number of trees on the field.
* `num_rocks`: The number of rocks on the field.
* `obstacles`: List storing obstacles (trees and rocks) and their properties.
* `OBSTACLE_TREE`: The identifier for trees.
* `OBSTACLE_ROCK`: The identifier for rocks.

### **Zombie Variables**

* `zombies`: List storing the position, angle, health, and state of each zombie.
* `zombie_radius`: The radius of a zombie for collision detection.
* `zombie_speed`: The speed at which zombies move.
* `zombie_damage`: The damage a zombie does when it hits the player.
* `zombie_health`: The health of a zombie.
* `zombie_spawn_timer`: Timer for spawning new zombies.
* `zombie_spawn_interval`: Time interval between zombie spawns.
* `zombie_kill_count`: The number of zombies killed by the player.
* `wave_zombie_limit`: The number of zombies in a wave.

### **Boss Variables**

* `boss`: The boss zombie’s attributes (position, health, state, etc.).
* `boss_radius`: The radius of the boss zombie.
* `boss_speed`: The speed of the boss zombie.
* `boss_damage`: The damage the boss does when it hits the player.
* `boss_max_health`: The maximum health of the boss.
* `boss_health`: The current health of the boss.
* `boss_projectile_cooldown`: Time between projectile attacks from the boss.
* `BOSS_HEALTHY`: State when the boss is at full health.
* `BOSS_WOUNDED`: State when the boss has lost some health.
* `BOSS_CRITICAL`: State when the boss is critically wounded.

### **Projectile Variables**

* `projectiles`: List storing the position, direction, and owner of each projectile.
* `projectile_speed`: The speed at which projectiles move.
* `projectile_radius`: The radius of projectiles.
* `PROJECTILE_PLAYER`: Flag for projectiles fired by the player.
* `PROJECTILE_BOSS`: Flag for projectiles fired by the boss.

### **Time Tracking Variables**

* `last_time`: The last time the game was updated.
* `time_delta`: The time difference between updates.

---

## **Functions**

### **Game Logic Functions**

* `init_game()`: Initializes the game by resetting the player’s stats and clearing entities.
* `generate_obstacles()`: Generates trees and rocks on the game field while ensuring no overlap with the player’s starting position.
* `spawn_zombie()`: Spawns a zombie at a random position on the field.
* `spawn_boss()`: Spawns the boss zombie at a random position on the field.
* `shoot_projectile(owner_type)`: Creates a new projectile fired by the player or boss.
* `check_collision(x, z, radius, exclude_player=False)`: Checks if a given position collides with any obstacles or the player.
* `update_player()`: Updates the player’s movement and checks for collisions.
* `update_zombies()`: Updates the zombies' movement and health, and checks if they collide with the player.
* `update_boss()`: Updates the boss zombie's movement, health, and attacks.
* `update_projectiles()`: Updates the projectiles' positions and checks for collisions with zombies or the player.
* `update_game_state()`: Updates the game state based on certain conditions like player health or boss defeat.

### **Drawing Functions**

* `draw_grid()`: Draws the floor grid for the game field.
* `draw_walls()`: Draws the boundary walls around the game field.
* `draw_obstacles()`: Draws trees and rocks on the field.
* `draw_player()`: Draws the player character.
* `draw_zombies()`: Draws all zombies on the field.
* `draw_boss()`: Draws the boss zombie, including health and limb status.
* `draw_projectiles()`: Draws all projectiles on the field.
* `draw_hud()`: Draws the heads-up display (HUD), including health and ammo status.
* `draw_menu()`: Draws the main menu screen.
* `draw_game_over()`: Draws the game over screen.

### **Camera Functions**

* `setup_camera()`: Sets up the camera view based on the current view mode (first-person or third-person).

### **GLUT Functions**

* `display()`: The main display function that handles all rendering.
* `idle()`: The idle function for continuous updates.
* `reshape()`: Handles window resizing and adjusts the viewport.
* `keyboard()`: Handles regular key presses (movement, shooting, etc.).
* `keyboard_up()`: Handles key releases for smooth movement.
* `special_keys()`: Handles special key presses (arrow keys).
* `special_keys_up()`: Handles special key releases.
* `mouse()`: Handles mouse clicks for shooting projectiles.
* `motion()`: Handles mouse movement for looking around (not fully implemented).

### **Initialization Functions**

* `init()`: Initializes OpenGL settings (background color, lighting, etc.).
* `main()`: Initializes GLUT, sets up the game, and starts the main loop.

---

## **Game Flow**

1. The game begins with the **main menu**. The player can press space to start the game.
2. The player controls the **player character** in a 3D environment, shooting projectiles at **zombies**.
3. The player must avoid obstacles and zombie attacks while keeping an eye on their **health** and **ammo**.
4. After defeating enough zombies, a **boss** zombie appears.
5. The game ends when the player’s health reaches zero. A **game over** screen is shown, displaying the player’s score.

---

## **Customization**

* **Zombies**: The player can adjust the zombie spawn rate, health, and damage to increase or decrease difficulty.
* **Boss**: The boss can be made more challenging by adjusting health and attack patterns.
* **Projectiles**: The speed and damage of projectiles can be modified to fine-tune combat mechanics.

---
