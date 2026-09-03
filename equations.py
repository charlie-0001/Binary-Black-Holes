import numpy


class BlackHoleData:
    def __init__(self):
        # constants
        self.gravitational_constant = 6.674e-11  # m^3 kg^-1 s^-2
        self.speed_of_light = 299792458  # m/s

        self.bh1_mass = 4e30
        self.bh2_mass = 4e30
        self.total_mass = self.bh1_mass + self.bh2_mass

        # initial conditions
        self.bh1_position = numpy.array([50000.0, 50000.0])
        self.bh2_position = numpy.array([-50000.0, -50000.0])
        self.initial_distance = self.distance_between_two_points(
            self.bh1_position, self.bh2_position
        )

        self.test_mass_position = numpy.array([1e22, 1e22])
        self.test_mass = 60

    def distance_between_two_points(self, pos1, pos2):
        return numpy.linalg.norm(pos1 - pos2)

    def calculate_separation_over_time(self, time):
        inner_term = (
            (self.initial_distance ** 4 - (256 / 5) *
             (
                 (self.gravitational_constant ** 3
                  * self.bh1_mass
                  * self.bh2_mass
                  * (self.bh1_mass + self.bh2_mass)
                  ) / self.speed_of_light ** 5) * time
             )
        )

        if inner_term <= 0:
            return 0.0

        return inner_term**0.25

    def get_angular_frequency(self, separation):
        if separation <= 0:
            return 0.0
        return numpy.sqrt(
            (self.gravitational_constant * self.total_mass) / (separation**3)
        )

    def get_positions(self, separation, phase):
        r_current = separation / 2.0
        bh1_x = r_current * numpy.cos(phase)
        bh1_y = r_current * numpy.sin(phase)

        bh1_pos = numpy.array([bh1_x, bh1_y])
        bh2_pos = -bh1_pos
        return bh1_pos, bh2_pos

    def strain_amplitude_changes_over_time(self, time):
        R = numpy.linalg.norm(self.test_mass_position)
        separation = self.calculate_separation_over_time(time)

        if separation <= 0:
            return 0.0

        return (
            4
            * (self.gravitational_constant**2)
            * self.bh1_mass
            * self.bh2_mass
        ) / ((self.speed_of_light**4) * R * separation)

    def waveform_over_time_plus(self, time, phase):
        return self.strain_amplitude_changes_over_time(time) * numpy.cos(2 * phase)

    def waveform_over_time_cross(self, time, phase):
        return self.strain_amplitude_changes_over_time(time) * numpy.sin(2 * phase)

    def calculate_velocity_difference(self, separation):
        if separation <= 0:
            return 0.0, 0.0, 0.0

        total_mass = self.bh1_mass + self.bh2_mass

        # standard newtonian orbital velocity
        v_newton = 0.5 * numpy.sqrt((self.gravitational_constant * total_mass) / separation)

        # relativistic orbital velocity (schwarzschild effective approximation)
        schwarzschild_radius = (2 * self.gravitational_constant * total_mass) / (self.speed_of_light ** 2)

        if separation <= schwarzschild_radius:
            return v_newton, self.speed_of_light, self.speed_of_light - v_newton

        v_rel = 0.5 * numpy.sqrt((self.gravitational_constant * total_mass) / (separation - schwarzschild_radius))
        v_rel = min(v_rel, self.speed_of_light)

        # calculate difference
        v_diff = v_rel - v_newton

        return v_newton, v_rel, v_diff


# -------------------------------------------------------


simulation = BlackHoleData()

divisor = 10000
dt = 1 / divisor
orbital_phase = 0.0

on = True

if on:
    for step in range(25000):
        t = step * dt
        current_distance = simulation.calculate_separation_over_time(t)

        if current_distance == 0:
            print(f"t={t:.4f}s: Black holes have merged.")
            break

        bh1_pos, bh2_pos = simulation.get_positions(current_distance, orbital_phase)

        h_plus = simulation.waveform_over_time_plus(t, orbital_phase)
        h_cross = simulation.waveform_over_time_cross(t, orbital_phase)

        print(f"t={t:.4f}s | Separation: {current_distance:.2f}m")
        print(f"   BH1 Position: [{bh1_pos[0]:.2f}, {bh1_pos[1]:.2f}]")
        print(f"   BH2 Position: [{bh2_pos[0]:.2f}, {bh2_pos[1]:.2f}]")
        print(
            f"   Phase: {orbital_phase:.2f} rad | h_plus: {h_plus:.2e} | h_cross: {h_cross:.2e}\n"
        )

        omega_current = simulation.get_angular_frequency(current_distance)
        orbital_phase += omega_current * dt