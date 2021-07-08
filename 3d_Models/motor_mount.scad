$fn = 10;

import("motor.stl");


difference() {
    translate([-(33 / 2), -15, 0]) {
        cube([33, 28, 2]);
    }
    cylinder(h = 13, r = 4);
}

rotate([-90, 0, 0]) {
    translate([-(33 / 2), -2, -16.5]) {
        cube([33, 70, 2]);
    }
}

translate([-(33 / 2), -16, -29.75]) {
    difference() {
        cube([2, 29, 30]);
        rotate([-45, 0, 0]) {
            translate([-1, -1, 0]) {
                cube([5, 45, 45]);
            }
       }
    }
}

translate([29 / 2, -16, -29.75]) {
    difference() {
        cube([2, 29, 30]);
        rotate([-45, 0, 0]) {
            translate([-1, -1, 0]) {
                cube([5, 45, 45]);
            }
       }
    }
}

translate([-24.5, -16.5, -22]) {
    difference() {
        cube([8, 2, 8]);
        translate([3.5, 2.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h = 3, r = 1);
            }
        }
    }
}

translate([16.5, -16.5, -22]) {
    difference() {
        cube([8, 2, 8]);
        translate([3.5, 2.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h = 3, r = 1);
            }
        }
    }
}

translate([-24.5, -16.5, -54]) {
    difference() {
        cube([8, 2, 8]);
        translate([3.5, 2.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h = 3, r = 1);
            }
        }
    }
}

translate([16.5, -16.5, -54]) {
    difference() {
        cube([8, 2, 8]);
        translate([3.5, 2.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h = 3, r = 1);
            }
        }
    }
}
