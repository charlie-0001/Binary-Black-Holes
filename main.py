import numpy


def distance_to_center_of_mass(target_mass, other_mass, total_separation) -> float:
    return (other_mass / (target_mass + other_mass)) * total_separation


def distance_between_two_points(pos1: numpy.ndarray, pos2: numpy.ndarray) -> float:
    return numpy.linalg.norm(pos1 - pos2)


gravitational_constant = 6.674 * (10 ** (-11))  # m^3 kg^(-1) s^(-2)
speed_of_light = 299792458 # m/s

bh1_position = numpy.array([3, 4])
bh1_mass = 4 * (10 ** 30)  # kg

bh2_position = numpy.array([-3, -4])
bh2_mass = 4 * (10 ** 30)  # kg

test_mass_position = numpy.array([1, 1])  # the observer
test_mass = 60  # kilograms

# -- calculations --

distance_between_black_holes = distance_between_two_points(bh1_position, bh2_position)
print("The distance between black holes 1 and 2 is: ", distance_between_black_holes)

bh1_distance_to_center_of_mass = distance_to_center_of_mass(bh1_mass, bh2_mass, distance_between_black_holes)
print("The distance between black hole 1 and the center of mass is: ", bh1_distance_to_center_of_mass)

angular_orbit_frequency = numpy.sqrt(
    (gravitational_constant * (bh1_mass + bh2_mass)) / (distance_between_black_holes ** 3))
print("Angular orbit frequency (rad/s): ", angular_orbit_frequency)


def bh_position_overtime(time: int, black_hole: int) -> numpy.ndarray:
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


print(f"Black hole 1 position (t=0): {bh_position_overtime(0, 1)}")
print(f"Black hole 2 position (t=0): {bh_position_overtime(0, 2)}")


def test_mass_newtonian_force_overtime(time: int) -> numpy.ndarray:

    r1_vector = test_mass_position - bh_position_overtime(time, 1)
    r2_vector = test_mass_position - bh_position_overtime(time, 2)

    r1_mag = numpy.linalg.norm(r1_vector)
    r2_mag = numpy.linalg.norm(r2_vector)

    force1 = -gravitational_constant * test_mass * bh1_mass * (r1_vector / (r1_mag ** 3))
    force2 = -gravitational_constant * test_mass * bh2_mass * (r2_vector / (r2_mag ** 3))

    return force1 + force2


def calculate_separation_over_time(time: float, initial_distance: float) -> float:

    loss_factor = (256.0 / 5.0) * ((gravitational_constant ** 3 * bh1_mass * bh2_mass * (bh1_mass + bh2_mass)) / (speed_of_light ** 5)) * time
    bracket_content = initial_distance ** 4 - loss_factor

    if bracket_content <= 0:
        return 0.0

    return bracket_content ** (1 / 4)


print("Test mass newtonian force vector (t=0) is: ", test_mass_newtonian_force_overtime(0))

print("--------------------------------------")
initial_distance = distance_between_two_points(bh1_position, bh2_position)
for t in range(0, 10000000, 1000000):
    current_distance = calculate_separation_over_time(t, initial_distance)

    print(f"t={t}: BH1 {bh_position_overtime(t, 1)}, BH2 {bh_position_overtime(t, 2)}")