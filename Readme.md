# Zombie Shooter 3D

A simple 3D zombie survival shooter built with Python and OpenGL. Navigate a field, collect health and ammo pickups, and face off against waves of zombies and a boss enemy under dynamic day/night lighting.

## Prerequisites

* **Python 3.x** installed and added to your system PATH.
* **Git** (for cloning the repository).

## Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/Sabidmahmud/Zombie_shooter.git
   cd Zombie_shooter
   ```

2. **Unzip the OpenGL assets**:

   * Locate the `OpenGL.zip` file in the project root.
   * Unzip its contents into the same directory, so you have:

     ```
     Zombie_shooter/
     ├── OpenGL/
     ├── Sec14_22299120-22201881-24241119-24241107_Spring2025.py 
     ├── ...
     ```
   * To unzip, run this command: 

     ```sh
     unzip OpenGL.zip     
     ```

3. **Prepare the main script**:
   The original game script is named `Sec14_22299120-22201881-24241119-24241107_Spring2025.py`. For ease of use, rename it:

   ```sh
   mv Sec14_22299120-22201881-24241119-24241107_Spring2025.py app.py
   ```

## Running the Game

With the OpenGL assets unzipped and script renamed, start the game by running:

```sh
python3 app.py
```

Use the following controls:

* **W/A/S/D** or **Arrow Keys**: Move
* **Q/E**: Rotate left/right
* **Spacebar**: Shoot / Start game
* **R**: Restart after Game Over

## Notes & Troubleshooting

* Ensure the `OpenGL/` folder (containing textures or shaders) is present at runtime.
* On some systems, you may need to install system OpenGL drivers or libraries (e.g., `sudo apt-get install libglu1-mesa-dev freeglut3-dev` on Debian/Ubuntu).
* If the window fails to open or crashes, try updating your graphics drivers or running in a clean environment.
* If you use wayland, the code could show and error `OpenGL.error.Error: Attempt to retrieve context when no valid context`. You need to enable XORG or x11 to run OpenGL projects.

## Documentation

For more detailed information about the codebase and team conventions, see:

* [Doc\_for\_team.md](./Doc_for_team.md)
