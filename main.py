import numpy


def distance_to_center_of_mass(target_mass, other_mass, total_separation) -> float:
    return (other_mass / (target_mass + other_mass)) * total_separation


def distance_between_two_points(pos1: numpy.ndarray, pos2: numpy.ndarray) -> float:
    return numpy.linalg.norm(pos1 - pos2)

gravitational_constant = 6.674 * (10 ** (-11))  # m^3 kg^(-1) s^(-2)
speed_of_light = 299792458  # m/s

bh1_position = numpy.array([1000000.0, 1000000.0]) # meters
bh1_mass = 4 * (10 ** 30)  # kg

bh2_position = numpy.array([-1000000.0, -1000000.0]) # meters
bh2_mass = 4 * (10 ** 30)  # kg

test_mass_position = numpy.array([1.0, 1.0])  # the observer
test_mass = 60  # kilograms

initial_distance = distance_between_two_points(bh1_position, bh2_position)

# -- calculations --

distance_between_black_holes = distance_between_two_points(bh1_position, bh2_position)
print("The distance between black holes 1 and 2 is: ", distance_between_black_holes)

bh1_distance_to_center_of_mass = distance_to_center_of_mass(bh1_mass, bh2_mass, distance_between_black_holes)
print("The distance between black hole 1 and the center of mass is: ", bh1_distance_to_center_of_mass)

angular_orbit_frequency = numpy.sqrt(
    (gravitational_constant * (bh1_mass + bh2_mass)) / (distance_between_black_holes ** 3))
print("Initial Angular orbit frequency (rad/s): ", angular_orbit_frequency)

def bh_position_overtime(time: float, black_hole: int) -> numpy.ndarray:
    if black_hole not in (1, 2):
        raise ValueError("Please insert 1 or 2 as a parameter.")

    x = bh1_position[0] * numpy.cos(angular_orbit_frequency * time) - bh1_position[1] * numpy.sin(
        angular_orbit_frequency * time)
    y = bh1_position[0] * numpy.sin(angular_orbit_frequency * time) + bh1_position[1] * numpy.cos(
        angular_orbit_frequency * time)

    if black_hole == 1:
        return numpy.array([x, y])
    if black_hole == 2:
        return numpy.array([-x, -y])

def calculate_separation_over_time(time: float) -> float:
    inner_term = (initial_distance ** 4 - (256 / 5) * ((gravitational_constant ** 3 * bh1_mass * bh2_mass * (
                bh1_mass + bh2_mass)) / speed_of_light ** 5) * time)
    if inner_term <= 0:
        return 0.0
    else:
        return inner_term ** (1 / 4)

def strain_amplitude_changes_over_time(time: float) -> float:
    # distance from origin (center of mass) to the observer
    R = numpy.linalg.norm(test_mass_position - numpy.array([0, 0]))
    d_t = calculate_separation_over_time(time)

    return (4 * (gravitational_constant ** 2) * bh1_mass * bh2_mass) / ((speed_of_light ** 4) * R * d_t)

def waveform_over_time_plus(time: float, phase: float) -> float:
    return strain_amplitude_changes_over_time(time) * numpy.cos(2 * phase)

def waveform_over_time_cross(time: float, phase: float) -> float:
    return strain_amplitude_changes_over_time(time) * numpy.sin(2 * phase)


print("--------------------------------------")

orbital_phase = 0.0
dt = 1  # loop step size in seconds
for t in range(0, 100, dt):
    current_distance = calculate_separation_over_time(t)

    omega_current = numpy.sqrt((gravitational_constant * (bh1_mass + bh2_mass)) / (current_distance ** 3))

    if current_distance == 0.0:
        print(f"t={t}s: Black holes have merged.")
        break

    if t > 0:
        orbital_phase += omega_current * dt

    h_plus = waveform_over_time_plus(t, orbital_phase)
    h_cross = waveform_over_time_cross(t, orbital_phase)

    print(f"t={t}s | Separation: {current_distance:.2f}m | Phase: {orbital_phase:.2f} rad | h_plus: {h_plus:.2e}")