# 화랑화살 1부 읽기 사이트

휴대폰에서 읽기 좋게 만든 「화랑화살 1부 · 과녁 뒤의 아이」 페이지입니다.
주소: https://maelong7.github.io/hwarang/

## 원고가 바뀌었을 때 다시 만드는 법

1. 원고 아티팩트의 index.html을 받아서 장을 뽑는다.
   `python3 tools/extract.py <원고 index.html> /tmp/chapters.json`
2. 페이지를 만든다. 마지막 값은 오프라인 캐시 이름이라 올릴 때마다 바꾼다.
   `python3 tools/build.py /tmp/chapters.json . https://maelong7.github.io/hwarang/ 202611192330`
3. 표지와 지도는 `img/cover.jpg`, `img/map-route.jpg`, `img/map-city.jpg`가 있으면 들어간다. 그림을 넣거나 바꾼 뒤에는 2번을 다시 한다.
4. 아이콘은 `python3 tools/render_art.py .`, 표지로 만든 링크 미리보기 그림(og.jpg)은 `python3 tools/render_og.py .`
