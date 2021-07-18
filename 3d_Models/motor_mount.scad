$fn = 10;

import("motor.stl");


difference() {
    translate([-(33 / 2), -14.5, 0]) {
        cube([33, 27.5, 3]);
    }
    translate([0, 0, -0.01]) {
        cylinder(h=5, r=4);
    }
}

translate([-(33 / 2), -14.75, -67]) {
    cube([33, 2, 70]);
}

translate([-(33 / 2), -14.75, -29.75]) {
    difference() {
        cube([3, 27.75, 30]);
        rotate([-45, 0, 0]) {
            translate([-1, -1.5, 0]) {
                cube([5, 45, 45]);
            }
       }
    }
}

translate([27 / 2, -14.75, -29.75]) {
    difference() {
        cube([3, 27.75, 30]);
        rotate([-45, 0, 0]) {
            translate([-1, -1.5, 0]) {
                cube([5, 45, 45]);
            }
       }
    }
}

translate([-24.5, -14.75, -22]) {
    difference() {
        cube([8, 3, 8]);
        translate([3.5, 3.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h=4, r=2);
            }
        }
    }
}

translate([16.5, -14.75, -22]) {
    difference() {
        cube([8, 3, 8]);
        translate([3.5, 3.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h=4, r=2);
            }
        }
    }
}

translate([-24.5, -14.75, -54]) {
    difference() {
        cube([8, 3, 8]);
        translate([3.5, 3.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h=4, r=2);
            }
        }
    }
}

translate([16.5, -14.75, -54]) {
    difference() {
        cube([8, 3, 8]);
        translate([3.5, 3.5, 4]) {
            rotate([90, 0, 0]) {
                cylinder(h=4, r=2);
            }
        }
    }
}
