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
        '<p><a href="us-canada.html"></p>' + "미국, 캐나다 최신뉴스</a> "+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=US&hl=ko"></p>'+ "미국 실시간 급상승 검색어</a>"+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=CA&hl=ko"></p>'+ "캐나다 실시간 급상승 검색어</a>",
    },
    {
      label: "Asia",
      name: "아시아",
      lat: 35.907757,
      lng: 127.766922,
      site:
        '<a href="asia.html">' + "아시아 최신뉴스</a> "+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=KR&hl=ko"></p>'+ "대한민국 실시간 급상승 검색어</a>"+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=JP&hl=ko"></p>'+ "일본 실시간 급상승 검색어</a>",
    },
    {
      label: "EU",
      name: "유럽",
      lat: 51.165691,
      lng: 10.451526,
      site:
        '<a href="europe.html">' + "유럽 최신뉴스</a> "+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=DE&hl=ko"></p>'+ "독일 실시간 급상승 검색어</a>"+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=IT&hl=ko"></p>'+ "이탈리아 실시간 급상승 검색어</a>"+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=FR&hl=ko"></p>'+ "프랑스 실시간 급상승 검색어</a>",
    },
    {
      label: "GB",
      name: "영국",
      lat: 55.378051,
      lng: -3.435973,
      site:
        '<a href="uk.html">' + "영국 최신뉴스</a> "+
        '<p><a href="https://trends.google.co.kr/trends/trendingsearches/daily?geo=GB&hl=ko"></p>'+ "영국 실시간 급상승 검색어</a>",
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
