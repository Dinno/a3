/**
 * Library for testing A3
 */

function setupSimpleScene() {
    var DEPTH         = 500;
    var WIDTH         = 500;
    var HEIGHT        = 500;
    var ASPECT        = 1;
    var NEAR          = 0.1;
    var FAR           = 3000;
    var VIEW_ANGLE    = 45;

    var container		= document.getElementById("container");

	renderer  = new A3.R(WIDTH, HEIGHT);
	scene     = new A3.Scene();
	camera    = new A3.Camera(VIEW_ANGLE, ASPECT, NEAR, FAR);
	
	camera.position.z = DEPTH;
	
	container.appendChild(renderer.domElement);		
}

