window.initMap = function () {
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,
    center: { lat: 49.496675, lng: -102.65625 },
  });

  const malls = [
    {
      label: "US, CA",
      name: "미국, 캐나다",
      lat: 37.09024,
      lng: -95.712891,
      site:
        '<a href="us-canada.html">' + "미국, 캐나다</a> ",
    },
    {
      label: "Asia",
      name: "아시아",
      lat: 35.907757,
      lng: 127.766922,
      site:
        '<a href="asia.html">' + "아시아</a> ",
    },
    {
      label: "EU",
      name: "유럽",
      lat: 51.165691,
      lng: 10.451526,
      site:
        '<a href="europe">' + "유럽</a> ",
    },
    {
      label: "GB",
      name: "영국",
      lat: 55.378051,
      lng: -3.435973,
      site:
        '<a href="uk.html">' + "영국</a> ",
    }
  ];

  const bounds = new google.maps.LatLngBounds();
  const infoWindow = new google.maps.InfoWindow();

  malls.forEach(({ label, name, lat, lng, site }) => {
    const marker = new google.maps.Marker({
      position: { lat, lng },
      label,
      map,
    });
    bounds.extend(marker.position);

    marker.addListener("click", () => {
      map.panTo(marker.position);
      infoWindow.setContent(site);
      infoWindow.open({
        anchor: marker,
        map,
      });
    });
  });

  map.fitBounds(bounds);
};
