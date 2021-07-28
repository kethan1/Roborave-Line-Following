$fn = 300;


difference() {
    translate([-(33 / 2), -15.5, 0]) {
        cube([33, 30, 3]);
    }
    translate([0, 0, -0.01]) {
        cylinder(h=5, r=3.8);
    }
    translate([0, 8.5, -0.1]) {
        cylinder(h=5, r=1.75);
    }
    translate([0, -8.5, -0.3]) {
        cylinder(h=15, r=1.75);
    }
    translate([8.5, 0, -0.1]) {
        cylinder(h=5, r=1.75);
    }
    translate([-8.5, 0, -0.1]) {
        cylinder(h=5, r=1.75);
    }
}

translate([-33 / 2, -15.75, -67]) {
    cube([33, 3, 70]);
}

translate([-33 / 2, -15.75, -29.75]) {
    difference() {
        cube([3, 30.25, 30]);
        rotate([-45, 0, 0]) {
            translate([-1, 0.35, 0]) {
                cube([5, 45, 45]);
            }
       }
    }
}

translate([27 / 2, -15.75, -29.75]) {
    difference() {
        cube([3, 30.25, 30]);
        rotate([-45, 0, 0]) {
            translate([-1, 0.35, 0]) {
                cube([5, 45, 45]);
            }
       }
    }
}

module screw_tabs(positive_side=true, top=false) {
    x_of_translate = positive_side ? 16.5 : -16.5 - 10;
    z_of_translate = top ? -22 : -54 ;
    translate([x_of_translate, -15.75, z_of_translate]) {
        difference() {
            translate([positive_side ? 0: 10, 3, 0]) {
                rotate([90, 0, 0]) {
                    cylinder(h=3, r=10);
                }
            }
            // cube([10, 3, 10]);
            translate([positive_side ? 4: 6, 3.5, 0]) {
                rotate([90, 0, 0]) {
                    cylinder(h=4, r=3.4);
                }
            }
        }
    }
}

screw_tabs();
screw_tabs(top=true);
screw_tabs(positive_side=false);
screw_tabs(positive_side=false, top=true);
