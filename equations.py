import numpy


class BlackHoleData:
    def __init__(self):
        # Constants
        self.gravitational_constant = 6.674e-11  # m^3 kg^-1 s^-2
        self.speed_of_light = 299792458  # m/s

        self.bh1_position = numpy.array([50000.0, 50000.0])
        self.bh2_position = numpy.array([-50000.0, -50000.0])

        self.bh1_mass = 4e30
        self.bh2_mass = 4e30

        self.test_mass_position = numpy.array([1e22, 1e22])
        self.test_mass = 60

        self.initial_distance = self.distance_between_two_points(
            self.bh1_position,
            self.bh2_position
        )

        self.angular_orbit_frequency = numpy.sqrt(
            (self.gravitational_constant * (self.bh1_mass + self.bh2_mass))
            / (self.initial_distance ** 3)
        )

    def distance_to_center_of_mass(self, target_mass, other_mass, total_separation):
        return (other_mass / (target_mass + other_mass)) * total_separation

    def distance_between_two_points(self, pos1, pos2):
        return numpy.linalg.norm(pos1 - pos2)

    def bh_position_overtime(self, time, black_hole):
        if black_hole not in (1, 2):
            raise ValueError("Please insert 1 or 2 as a parameter.")

        x = (
            self.bh1_position[0] * numpy.cos(self.angular_orbit_frequency * time)
            - self.bh1_position[1] * numpy.sin(self.angular_orbit_frequency * time)
        )

        y = (
            self.bh1_position[0] * numpy.sin(self.angular_orbit_frequency * time)
            + self.bh1_position[1] * numpy.cos(self.angular_orbit_frequency * time)
        )

        if black_hole == 1:
            return numpy.array([x, y])

        return numpy.array([-x, -y])

    def calculate_separation_over_time(self, time):
        inner_term = (
            self.initial_distance ** 4
            - (256 / 5)
            * (
                (
                    self.gravitational_constant ** 3
                    * self.bh1_mass
                    * self.bh2_mass
                    * (self.bh1_mass + self.bh2_mass)
                )
                / self.speed_of_light ** 5
            )
            * time
        )

        if inner_term <= 0:
            return 0.0

        return inner_term ** 0.25

    def strain_amplitude_changes_over_time(self, time):
        R = numpy.linalg.norm(self.test_mass_position)

        separation = self.calculate_separation_over_time(time)

        return (
            4
            * (self.gravitational_constant ** 2)
            * self.bh1_mass
            * self.bh2_mass
        ) / (
            (self.speed_of_light ** 4)
            * R
            * separation
        )

    def waveform_over_time_plus(self, time, phase):
        return self.strain_amplitude_changes_over_time(time) * numpy.cos(2 * phase)

    def waveform_over_time_cross(self, time, phase):
        return self.strain_amplitude_changes_over_time(time) * numpy.sin(2 * phase)


# -------------------------------------------------------

simulation = BlackHoleData()

divisor = 10000
orbital_phase = 0.0
dt = 1 / divisor

on = False

if on:
    for t in range(25000):
        t /= divisor

        current_distance = simulation.calculate_separation_over_time(t)

        if current_distance == 0:
            print(f"t={t}s: Black holes have merged.")
            break

        r_current = current_distance / 2

        bh1_x = r_current * numpy.cos(orbital_phase)
        bh1_y = r_current * numpy.sin(orbital_phase)

        bh1_pos_current = numpy.array([bh1_x, bh1_y])
        bh2_pos_current = -bh1_pos_current

        h_plus = simulation.waveform_over_time_plus(t, orbital_phase)
        h_cross = simulation.waveform_over_time_cross(t, orbital_phase)

        print(f"t={t}s | Separation: {current_distance:.2f}m")
        print(f"   BH1 Position: [{bh1_pos_current[0]:.2f}, {bh1_pos_current[1]:.2f}]")
        print(f"   BH2 Position: [{bh2_pos_current[0]:.2f}, {bh2_pos_current[1]:.2f}]")
        print(f"   Phase: {orbital_phase:.2f} rad | h_plus: {h_plus:.2e} | h_cross: {h_cross:.2e}\n")

        omega_current = numpy.sqrt(
            (simulation.gravitational_constant * (simulation.bh1_mass + simulation.bh2_mass))
            / (current_distance ** 3)
        )

        orbital_phase += omega_current * dt