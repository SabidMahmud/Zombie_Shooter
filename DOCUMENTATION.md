# **3D Zombie Shooter Game Documentation**

## **Overview**

This 3D Zombie Shooter game is an action-packed survival game where the player must defend against waves of zombies. The player can shoot, move, and interact with the environment while trying to survive as long as possible. The game progresses through various levels, with a **boss zombie** appearing after the player kills a certain number of zombies.

This documentation covers the gameplay, mechanics, environment setup, controls, and future updates for weapons. The **weapon variations** feature is planned for a future update.

---

## **Table of Contents**

1. [Gameplay Overview](#gameplay-overview)
2. [Game Mechanics](#game-mechanics)

   * [Movement](#movement)
   * [Shooting](#shooting)
   * [Zombies and Bosses](#zombies-and-bosses)
   * [Pickups (Health and Ammo)](#pickups-health-and-ammo)
   * [Game States](#game-states)
   * [Lighting (Day/Night)](#lighting-daynight)
3. [Game Environment](#game-environment)

   * [Field and Boundaries](#field-and-boundaries)
   * [Obstacles](#obstacles)
4. [Controls](#controls)

   * [Keyboard Controls](#keyboard-controls)
   * [Mouse Controls](#mouse-controls)
5. [Future Updates](#future-updates)
6. [Known Issues](#known-issues)

---

## **Gameplay Overview**

The 3D Zombie Shooter game is a survival-style game in which the player must fend off waves of zombies. The player controls a character armed with a weapon (which will be upgraded in future updates) and must navigate a 3D world filled with obstacles, health pickups, ammo pickups, and zombie enemies.

As the game progresses, the difficulty increases, with the appearance of **boss zombies** that are more challenging to defeat. The game features a dynamic **day and night cycle**, with the lighting transitioning based on whether the boss is present.

---

## **Game Mechanics**

### **Movement**

The player can move through the environment using standard first-person or third-person controls. The player can move forward, backward, strafe left or right, and rotate in place.

* **Movement Flags**: The player's movement is controlled using flags like `move_forward`, `move_backward`, `strafe_left`, and `strafe_right`.
* **Player Speed**: The player’s movement speed is defined by `player_speed`, allowing the player to navigate the field quickly.

### **Shooting**

The player can shoot projectiles at zombies or other enemies in the environment.

* **Cooldown Mechanism**: There is a **cooldown period** between shots, controlled by `shot_cooldown` to simulate realistic firing rates.
* **Ammo**: The player has a limited amount of **ammo**, which decreases as they shoot and can be replenished with ammo pickups.

### **Zombies and Bosses**

Zombies are the primary enemies in the game. They spawn periodically and approach the player, dealing damage if they get too close.

* **Zombie Types**: Zombies vary in health and damage, and they increase in difficulty as the player advances to higher levels.
* **Boss Zombies**: A **boss zombie** will spawn after the player kills a set number of regular zombies. Boss zombies have much higher health and deal more damage, significantly increasing the challenge.
* **Zombie Spawning**: Zombies spawn at random positions within a predefined distance from the player.

### **Pickups (Health and Ammo)**

Pickups are scattered across the field to help the player recover health and ammo.

* **Health Pickups**: Health pickups restore a portion of the player’s health. They expire after a fixed amount of time if not collected.
* **Ammo Pickups**: Ammo pickups provide a set amount of ammo to the player’s weapon. These also expire after a set period.

### **Game States**

The game operates in one of several states:

* **Menu**: The game is at the start screen, and the player can press a key to start the game.
* **Playing**: The player is actively engaging with zombies and navigating the environment.
* **Game Over**: The player has died, and the game ends. The player can press `R` to restart.

### **Lighting (Day/Night)**

The game has a **dynamic lighting system** that transitions between day and night.

* **Daytime Lighting**: During the normal gameplay (before the boss appears), the environment is lit with **daytime** lighting (ambient light is set to `day_ambient`).
* **Nighttime Lighting**: Once the boss zombie is spawned, the game switches to **nighttime** lighting (ambient light is set to `night_ambient`), adding to the game's tension.

---

## **Game Environment**

### **Field and Boundaries**

The game world consists of a large square grid (the **field**) on which the player can move.

* **Field Size**: The size of the field is determined by `field_size`. The player and zombies are constrained to this area.
* **Walls/Boundaries**: The field is surrounded by **walls** to keep the player within the game area. The walls are created using cubes and placed at the edges of the grid.

### **Obstacles**

Various **obstacles** such as **trees** and **rocks** are scattered across the field. These obstacles block the player’s movement and create strategic barriers for both the player and zombies.

* **Obstacle Types**:

  * **Trees**: Represented as cubes and cones.
  * **Rocks**: Represented as spheres.
* **Random Generation**: Obstacles are generated randomly within a safe radius from the player’s starting position.

---

## **Controls**

### **Keyboard Controls**

* **W**: Move forward.
* **S**: Move backward.
* **A**: Strafe left.
* **D**: Strafe right.
* **Q**: Turn left.
* **E**: Turn right.
* **Spacebar**: Shoot (if ammo is available).
* **R**: Restart the game after game over.

### **Mouse Controls**

* **Left Mouse Button**: Shoot projectile (while in playing state).
* **Right Mouse Button**: (Planned future update for weapon selection).

---

## **Future Updates**

### **Weapon Variations**

The game will include **weapon variations** in future updates. These weapons will differ in damage, fire rate, ammo capacity, and more. The weapon variations will be represented as pickups and available for the player to collect during gameplay.

Planned weapon types include:

* **Pistol**: Low damage, high fire rate, low ammo capacity.
* **Rifle**: Moderate damage, slower fire rate, higher ammo capacity.
* **Shotgun**: High damage, low fire rate, high ammo capacity but limited range.

These variations will be equipped by the player based on pickups found in the game world.

---

## **Known Issues**

* **Weapon Variations**: Currently, the weapon variation system is not implemented. The game will only feature a basic shooting mechanic until the update is released.
* **AI Pathfinding**: Zombies sometimes get stuck in obstacles. Improvements to AI pathfinding will be made in future updates to ensure smoother movement.
* **Lighting Transition**: The lighting transition between day and night when the boss spawns could be smoother and more visually appealing.

---

## **Conclusion**

This documentation outlines the core gameplay, mechanics, environment setup, and controls for the 3D Zombie Shooter game. The game offers exciting action, with an increasing challenge through waves of zombies and bosses, along with interactive elements like pickups and obstacles. Future updates will enhance the gameplay with more weapon variations and improved features.
