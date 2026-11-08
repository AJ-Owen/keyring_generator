// #################################
NAME = "{{NAME}}";
// Full path to the icon, or empty for a keyring without an icon
ICON = "{{ICON}}";
// "body", "inlay" or "all" - set via -D PART="..." when exporting
PART = "all";
// #################################

icon_width = ICON == "" ? 0 : 15;
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
    translate([text_width/2,depth/2])
    text(str(" ", NAME), halign="center", valign="center", font="Ubuntu Mono:style=Extra Bold Italic", size=8);
}

module keyring_hole(){
    translate([2, depth/2, -corner_radius*4])
    linear_extrude(corner_radius*8)
    circle(r=(keyring_radius-1));
}

module icon(){
    if (ICON != "")
    translate([text_width+(icon_width/2),depth/2])
    //rotate(180)
    scale(0.06)
    import(ICON, center=true);
}

// Text and icon outline, extruded down from the top surface (z=0) of the body
module inlay(height=thickness){
    translate([0, 0, -thickness])
    linear_extrude(height)
    {
        name_text();
        icon();
    }
}

module tag(){
    difference(){
        body();
        keyring_hole();
        // Extend the cut above the surface to avoid coplanar faces
        inlay(thickness + 1);
    }
}


if (PART == "body" || PART == "all") color("black") tag();
if (PART == "inlay" || PART == "all") color("orange") inlay();

//bone();
