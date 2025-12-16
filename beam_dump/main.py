import pyray as rl
import random
import math
import json
from collections import deque
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class TargetDistribution:
    mean_x: float = 0.0
    mean_y: float = 0.0
    std_x: float = 0.0
    std_y: float = 0.0
    rms_radius: float = 0.0
    max_deviation: float = 0.0
    total_particles: int = 0

    def update(self, particles_data: deque):
        if len(particles_data) == 0:
            return

        x_vals = [p[0] for p in particles_data]
        y_vals = [p[1] for p in particles_data]
        distances = [p[3] for p in particles_data]

        self.total_particles = len(particles_data)
        self.mean_x = sum(x_vals) / self.total_particles
        self.mean_y = sum(y_vals) / self.total_particles

        var_x = sum((x - self.mean_x) ** 2 for x in x_vals) / self.total_particles
        var_y = sum((y - self.mean_y) ** 2 for y in y_vals) / self.total_particles
        self.std_x = math.sqrt(var_x)
        self.std_y = math.sqrt(var_y)

        self.rms_radius = math.sqrt(
            sum(x**2 + y**2 for x, y in zip(x_vals, y_vals)) / self.total_particles
        )
        self.max_deviation = max(distances)


@dataclass
class SteeringMagnet:
    z_position: float
    name: str
    kick_x: float = 0.0
    kick_y: float = 0.0
    strength: float = 1.0
    is_corrector: bool = True

    def get_effective_kick_x(self, jitter: float = 0.0) -> float:
        return self.kick_x + random.gauss(0, jitter)

    def get_effective_kick_y(self, jitter: float = 0.0) -> float:
        return self.kick_y + random.gauss(0, jitter)


SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 900
CAMERA_DISTANCE = 50.0

STEERING_MAGNETS = [
    SteeringMagnet(0.0, "Injector Corrector", strength=0.8),
    SteeringMagnet(12.0, "H-Corrector 1", strength=1.0),
    SteeringMagnet(24.0, "V-Corrector 1", strength=1.0),
    SteeringMagnet(36.0, "H-Corrector 2", strength=1.2),
    SteeringMagnet(48.0, "Final Corrector", strength=1.0),
    SteeringMagnet(60.0, "Beam Dump", strength=0.0, is_corrector=False),
]

particles = deque(maxlen=2000)


class Camera3D:
    def __init__(self):
        self.distance = CAMERA_DISTANCE
        self.rotation_x = 20.0
        self.rotation_y = -30.0
        self.target = rl.Vector3(0, 0, 25)
        self.is_panning = False
        self.last_mouse_pos = rl.Vector2(0, 0)

    def update(self):
        if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
            self.is_panning = True
            self.last_mouse_pos = rl.get_mouse_position()
        elif rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
            self.is_panning = False

        if self.is_panning:
            mouse_pos = rl.get_mouse_position()
            delta_x = mouse_pos.x - self.last_mouse_pos.x
            delta_y = mouse_pos.y - self.last_mouse_pos.y

            self.rotation_y += delta_x * 0.5
            self.rotation_x += delta_y * 0.5
            self.rotation_x = max(-89, min(89, self.rotation_x))
            self.last_mouse_pos = mouse_pos

    def get_camera(self):
        rad_x = math.radians(self.rotation_x)
        rad_y = math.radians(self.rotation_y)

        cam_x = self.target.x + self.distance * math.cos(rad_x) * math.sin(rad_y)
        cam_y = self.target.y + self.distance * math.sin(rad_x)
        cam_z = self.target.z + self.distance * math.cos(rad_x) * math.cos(rad_y)

        camera = rl.Camera3D(
            rl.Vector3(cam_x, cam_y, cam_z),
            self.target,
            rl.Vector3(0, 1, 0),
            45.0,
            rl.CameraMode.CAMERA_FREE,
        )
        return camera


def get_heatmap_color(distance, max_distance=2.0):
    normalized = min(distance / max_distance, 1.0)
    if normalized < 0.5:
        r = 0
        g = int(255 * (normalized * 2))
        b = int(255 * (1 - normalized * 2))
    else:
        r = int(255 * ((normalized - 0.5) * 2))
        g = int(255 * (1 - (normalized - 0.5) * 2))
        b = 0
    return rl.Color(r, g, b, 200)


def calculate_beam_trajectory(
    z: float,
    magnets: List[SteeringMagnet],
    start_x: float = 0.2,
    start_y: float = 0.6,
    emittance_x: float = 2.0,
    emittance_y: float = 4.0,
    magnet_jitter_x: float = 0.05,
    magnet_jitter_y: float = 0.5,
) -> tuple:
    x = start_x
    y = start_y
    angle_x = random.gauss(0, emittance_x)
    angle_y = random.gauss(0, emittance_y)

    last_z = 0.0

    for magnet in magnets:
        if magnet.z_position > z:
            drift = z - last_z
            x += angle_x * 0.001 * drift
            y += angle_y * 0.001 * drift
            break

        drift = magnet.z_position - last_z
        x += angle_x * 0.001 * drift
        y += angle_y * 0.001 * drift

        if magnet.is_corrector:
            angle_x += magnet.get_effective_kick_x(magnet_jitter_x) * magnet.strength
            angle_y += magnet.get_effective_kick_y(magnet_jitter_y) * magnet.strength

        last_z = magnet.z_position

    return (x, y, angle_x, angle_y)


def draw_steering_magnet(magnet: SteeringMagnet, is_selected: bool):
    size = 15.0
    divisions = 5
    color = (
        rl.MAGENTA
        if is_selected and magnet.is_corrector
        else rl.Color(255, 255, 255, 30)
    )

    for i in range(divisions + 1):
        offset = -size / 2 + (size / divisions) * i
        rl.draw_line_3d(
            rl.Vector3(-size / 2, offset, magnet.z_position),
            rl.Vector3(size / 2, offset, magnet.z_position),
            color,
        )
        rl.draw_line_3d(
            rl.Vector3(offset, -size / 2, magnet.z_position),
            rl.Vector3(offset, size / 2, magnet.z_position),
            color,
        )

    if magnet.is_corrector and (abs(magnet.kick_x) > 0.1 or abs(magnet.kick_y) > 0.1):
        arrow_scale = 0.5
        arrow_x = magnet.kick_x * arrow_scale
        arrow_y = magnet.kick_y * arrow_scale
        rl.draw_line_3d(
            rl.Vector3(0, 0, magnet.z_position),
            rl.Vector3(arrow_x, arrow_y, magnet.z_position),
            rl.Color(255, 165, 0, 255),
        )


def draw_beam_trajectory(magnets: List[SteeringMagnet]):
    num_segments = 1000
    z_start = 0
    z_end = magnets[-1].z_position

    for i in range(num_segments):
        z1 = z_start + (z_end - z_start) * i / num_segments
        z2 = z_start + (z_end - z_start) * (i + 1) / num_segments

        x1, y1, _, _ = calculate_beam_trajectory(z1, magnets)
        x2, y2, _, _ = calculate_beam_trajectory(z2, magnets)

        rl.draw_line_3d(
            rl.Vector3(x1, y1, z1), rl.Vector3(x2, y2, z2), rl.Color(0, 255, 255, 180)
        )

    envelope_samples = 20
    for i in range(envelope_samples):
        z = z_start + (z_end - z_start) * i / envelope_samples
        x, y, _, _ = calculate_beam_trajectory(z, magnets)
        radius = 0.3
        rl.draw_circle_3d(
            rl.Vector3(x, y, z),
            radius,
            rl.Vector3(0, 0, 1),
            90.0,
            rl.Color(0, 255, 255, 30),
        )


def draw_ui(
    selected_magnet_idx: int,
    magnets: List[SteeringMagnet],
    target_dist: TargetDistribution,
):
    rl.draw_text(
        "Beamline Control Simulator",
        10,
        10,
        24,
        rl.RAYWHITE,
    )
    y_pos = 45
    rl.draw_text("Camera Controls:", 10, y_pos, 18, rl.RAYWHITE)
    y_pos += 25
    rl.draw_text("Right Mouse: Rotate view", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 30
    rl.draw_text("Steering Controls:", 10, y_pos, 18, rl.RAYWHITE)
    y_pos += 25
    rl.draw_text("1-6: Select corrector magnet", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 20
    rl.draw_text("Arrow Keys: Adjust H/V kicks", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 20
    rl.draw_text("Shift+Arrows: Fine adjustment", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 20
    rl.draw_text("R: Reset selected magnet", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 20
    rl.draw_text("0: Reset all magnets", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 20
    rl.draw_text("C: Clear particles", 15, y_pos, 14, rl.RAYWHITE)
    y_pos += 20
    rl.draw_text("D: Dump params to console (JSON)", 15, y_pos, 14, rl.RAYWHITE)

    info_x = SCREEN_WIDTH - 400
    y_pos = 45
    rl.draw_text("Target Distribution", info_x, y_pos, 18, rl.RAYWHITE)
    y_pos += 25
    rl.draw_text(
        f"RMS Radius: {target_dist.rms_radius:.3f} m",
        info_x,
        y_pos,
        13,
        rl.RAYWHITE,
    )
    y_pos += 18
    rl.draw_text(
        f"Max Dev: {target_dist.max_deviation:.3f} m",
        info_x,
        y_pos,
        13,
        rl.RAYWHITE,
    )
    y_pos += 30

    rl.draw_text("Steering Magnets", info_x, y_pos, 18, rl.RAYWHITE)
    y_pos += 25
    for i, magnet in enumerate(magnets):
        if not magnet.is_corrector:
            continue
        color = rl.Color(255, 255, 0, 255) if i == selected_magnet_idx else rl.RAYWHITE
        status = f"({magnet.kick_x:+.1f}, {magnet.kick_y:+.1f})"
        rl.draw_text(f"{i+1}. {magnet.name} {status}", info_x, y_pos, 13, color)
        y_pos += 18

    if 0 <= selected_magnet_idx < len(magnets):
        magnet = magnets[selected_magnet_idx]
        if magnet.is_corrector:
            y_pos += 10
            rl.draw_text(
                f"Position: Z = {magnet.z_position:.1f} m",
                info_x,
                y_pos,
                14,
                rl.RAYWHITE,
            )
            y_pos += 20
            rl.draw_text(
                f"H-Kick: {magnet.kick_x:.2f} mrad",
                info_x,
                y_pos,
                14,
                rl.RAYWHITE,
            )
            y_pos += 20
            rl.draw_text(
                f"V-Kick: {magnet.kick_y:.2f} mrad",
                info_x,
                y_pos,
                14,
                rl.RAYWHITE,
            )
            y_pos += 20
            rl.draw_text(
                f"Strength: {magnet.strength:.1f}",
                info_x,
                y_pos,
                14,
                rl.RAYWHITE,
            )
            y_pos += 20
            rl.draw_text(
                f"Type: {'Corrector' if magnet.is_corrector else 'Dump'}",
                info_x,
                y_pos,
                14,
                rl.RAYWHITE,
            )


def dump_system_state(
    magnets: List[SteeringMagnet],
    target_dist: TargetDistribution,
):
    state = {
        "timestamp": rl.get_time(),
        "target_distribution": asdict(target_dist),
        "magnets": [
            {
                "name": m.name,
                "z_position": m.z_position,
                "kick_x_mrad": m.kick_x,
                "kick_y_mrad": m.kick_y,
                "strength": m.strength,
                "is_corrector": m.is_corrector,
            }
            for m in magnets
        ],
    }
    print(json.dumps(state, indent=2))


def main():
    rl.set_config_flags(rl.ConfigFlags.FLAG_BORDERLESS_WINDOWED_MODE)
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_UNDECORATED)
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Beamline Control Simulator")
    rl.set_target_fps(60)

    camera_3d = Camera3D()
    selected_magnet_idx = 0
    target_dist = TargetDistribution()

    while not rl.window_should_close():
        camera_3d.update()

        for i in range(min(len(STEERING_MAGNETS), 9)):
            if rl.is_key_pressed(rl.KeyboardKey.KEY_ONE + i):
                selected_magnet_idx = i

        if 0 <= selected_magnet_idx < len(STEERING_MAGNETS):
            magnet = STEERING_MAGNETS[selected_magnet_idx]

            if magnet.is_corrector:
                is_fine = rl.is_key_down(
                    rl.KeyboardKey.KEY_LEFT_SHIFT
                ) or rl.is_key_down(rl.KeyboardKey.KEY_RIGHT_SHIFT)
                kick_step = 0.1 if is_fine else 0.5

                if rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
                    magnet.kick_x -= kick_step
                if rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
                    magnet.kick_x += kick_step
                if rl.is_key_down(rl.KeyboardKey.KEY_UP):
                    magnet.kick_y += kick_step
                if rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
                    magnet.kick_y -= kick_step

                max_kick = 20.0
                magnet.kick_x = max(-max_kick, min(max_kick, magnet.kick_x))
                magnet.kick_y = max(-max_kick, min(max_kick, magnet.kick_y))

                if rl.is_key_pressed(rl.KeyboardKey.KEY_R):
                    magnet.kick_x = 0.0
                    magnet.kick_y = 0.0

        if rl.is_key_pressed(rl.KeyboardKey.KEY_ZERO):
            for magnet in STEERING_MAGNETS:
                magnet.kick_x = 0.0
                magnet.kick_y = 0.0

        if rl.is_key_pressed(rl.KeyboardKey.KEY_C):
            particles.clear()

        if rl.is_key_pressed(rl.KeyboardKey.KEY_D):
            dump_system_state(STEERING_MAGNETS, target_dist)

        dump_magnet = STEERING_MAGNETS[-1]
        px, py, _, _ = calculate_beam_trajectory(
            dump_magnet.z_position, STEERING_MAGNETS
        )

        ideal_x = 0
        ideal_y = 0
        distance = math.sqrt((px - ideal_x) ** 2 + (py - ideal_y) ** 2)
        particles.append((px, py, dump_magnet.z_position, distance))

        target_dist.update(particles)

        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

        camera = camera_3d.get_camera()
        rl.begin_mode_3d(camera)

        for i, magnet in enumerate(STEERING_MAGNETS):
            draw_steering_magnet(magnet, i == selected_magnet_idx)

        draw_beam_trajectory(STEERING_MAGNETS)

        for px, py, pz, dist in particles:
            color = get_heatmap_color(dist)
            rl.draw_sphere(rl.Vector3(px, py, pz), 0.12, color)

        rl.end_mode_3d()

        draw_ui(selected_magnet_idx, STEERING_MAGNETS, target_dist)

        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    main()
