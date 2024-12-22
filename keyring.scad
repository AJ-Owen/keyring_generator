// #################################
NAME = "{{NAME}}";
// #################################

icon_width = 15;
text_width = len(NAME)*7 + 5;
width = icon_width + text_width;
depth = 15;
thickness = 1;
corner_radius = 1.5;
keyring_radius = 4;

// For 3d printing
$fa = 1;
$fs = 0.4;



module body(){
    hull()
    {
        translate([0, 0, -corner_radius]) sphere(r=corner_radius);
        translate([0, depth, -corner_radius]) sphere(r=corner_radius);
        translate([width, 0, -corner_radius]) sphere(r=corner_radius);
        translate([width, depth, -corner_radius]) sphere(r=corner_radius);
        translate([0, depth/2, -corner_radius*2])
        linear_extrude(corner_radius*2)
        circle(r=keyring_radius);
    }
}

module name_text(){
    linear_extrude(thickness)
    translate([text_width/2,depth/2,-0.001])
    color("turquoise")
    text(str(" ", NAME), halign="center", valign="center", font="Ubuntu Mono:style=Extra Bold Italic", size=8);
}

module keyring_hole(){
    translate([2, depth/2, -corner_radius*4])
    linear_extrude(corner_radius*8)
    circle(r=(keyring_radius-1));
}

module tag(){
    difference(){
        body();
        keyring_hole();
    }

    name_text();
}

module icon(){
    translate([text_width+(icon_width/2),depth/2,0])
    linear_extrude(thickness)
    //rotate(180)
    scale(0.06)
    import("/home/josh/repos/keyring_generator/icons/{{ICON}}", center=true);
}


tag();
icon();

//bone();
