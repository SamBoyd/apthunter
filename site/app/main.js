let popupTemplate = require('popup');

$(function() {
	let map = L.map('map').setView([51.505, -0.09], 13);

	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);

	$.get('data.txt', function(data) {
		let lines = data.split('\n');
		lines.forEach(function(line) {
			try {
				if(!! /\S/.test(line)) {
					console.log(line)
					let myData = JSON.parse(line);
					myData['page_urls'] = eval(myData['page_urls'])
					myData['coordinates'].forEach(function(coordinate) {
						let coordSplit = coordinate.split(' ');
						let coordFormatted = [parseFloat(coordSplit[0]), parseFloat(coordSplit[1])];
						L.marker(coordFormatted).addTo(map)
						    .bindPopup(popupTemplate(myData))
						    .openPopup();
					});
				}
			} catch (e) {
				console.log('failed to parse ' + line);
			}
		});
	});

});
