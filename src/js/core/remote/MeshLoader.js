/**
 * @class Loads in a resource file over AJAX <strong>[A3.MeshLoader]</strong>.
 * Handy for the loading of mesh data files
 * 
 * @author Paul Lewis
 * 
 * @param {String} url The URL to load
 * @param {Function} callback The callback to which the geometry should be passed
 */

A3.Core.Remote.JSON = {

	/**
	 * Imports geometry from A3 JSON representation
	 */
	importGeometry: function(data) {
		var 
			vertexArray   = null,
			vertices      = [],
			faces         = [],
			colors        = [],
			faceArray     = null,
			faceData      = null,
			face          = null,
			uvs           = [],
			uvArray	      = null,
			uvDataBlock		= null,
			v             = 0,
			f             = 0,
			uv            = 0;

		vertexArray    = data.vertices;
		faceArray      = data.faces;
		uvArray        = data.uvs;
		
//		alert('(data) name: ' + data.name
//				+ ' vert:' + vertexArray.length
//				+ ' faces:' + faceArray.length 
//				+ ' uvs:' + uvArray.length);

		// go through the vertices
		for(v = 0; v < vertexArray.length; v++) {
			vertexData = vertexArray[v];
			vertices.push(
				new A3.Vertex(vertexData[0], vertexData[1], vertexData[2])
			);
		}
		
		// now go through the faces
		for(f = 0; f < faceArray.length; f++) {
			faceData = faceArray[f];
			
			if(faceData.length === 3) {
				face = new A3.Face3(faceData[0], faceData[1], faceData[2]);
			} else if(faceData.length === 4) {
				face = new A3.Face4(faceData[0], faceData[1], faceData[2], faceData[3]);
			}
			faces.push(face);
		}
		
		// and the uv data
		if(!!uvArray && !!uvArray.length) {
			for(uv = 0; uv < uvArray.length; uv++) {
				uvDataBlock = uvArray[uv];
				uvs.push(
					new A3.V2(uvDataBlock[0], uvDataBlock[1])
				);
			}
		}

		// return a geometry
		return new A3.Geometry({
			vertices: vertices,
			faces: faces,
			colors: colors,
			faceUVs: uvs
		});
	}
};

A3.Core.Remote.MeshLoader = function(url, callback) {
	
	var request	= new XMLHttpRequest();


	request.onreadystatechange = function() {
		if(request.readyState === 4) {
			data = JSON.parse(request.responseText);
			
			// call the callback
			if(!!callback) {
				callback(A3.Core.Remote.JSON.importGeometry(data));
			}
		}
	};
	
	/**
	 * Dispatches the request for the data
	 */
	this.load = function() {
		request.open("GET", url, true);
		request.send(null);
	};
};

// shortcut
A3.MeshLoader = A3.Core.Remote.MeshLoader;
