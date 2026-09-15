document.addEventListener('DOMContentLoaded', () => {
    const panel = document.querySelector('.planner');
    const panelContent = document.getElementById('panel-content');
    const panelToggle = document.getElementById('panel-toggle');
    const mapStatus = document.getElementById('map-status');
    const form = document.getElementById('route-form');
    const submitButton = document.getElementById('find-route');
    const submitLabel = document.getElementById('submit-label');
    const routePayload = document.getElementById('route-coordinates');
    const routeCoordinates = routePayload ? JSON.parse(routePayload.textContent) : [];
    const tokenPayload = document.getElementById('mapbox-public-token');
    const mapboxToken = tokenPayload ? JSON.parse(tokenPayload.textContent) : '';
    const compactScreen = window.matchMedia('(max-width: 640px)');
    let map;
    let routeBounds;

    function setPanelExpanded(expanded) {
        panelContent.hidden = !expanded;
        panelToggle.setAttribute('aria-expanded', String(expanded));
        panelToggle.setAttribute('aria-label', expanded ? 'Minimize route planner' : 'Expand route planner');
    }
    panelToggle.hidden = false;
    // Keep successful routes visible on smaller screens; errors stay expanded.
    if (compactScreen.matches && routeCoordinates.length > 1) setPanelExpanded(false);
    panelToggle.addEventListener('click', () => {
        setPanelExpanded(panelContent.hidden);
        if (routeBounds) fitRoute();
    });
    window.MaritimeInterface.initialize();
    form.addEventListener('submit', event => {
        if (!window.MaritimeInterface.validateRouteForm(form)) {
            event.preventDefault();
            return;
        }
        submitButton.disabled = true;
        submitLabel.textContent = 'Finding route…';
        form.setAttribute('aria-busy', 'true');
    });
    window.addEventListener('pageshow', () => {
        submitButton.disabled = false;
        submitLabel.textContent = 'Find route';
        form.removeAttribute('aria-busy');
    });
    function showMapError() {
        mapStatus.textContent = 'The map could not load. Check your connection and reload the page.';
        mapStatus.hidden = false;
    }
    if (!mapboxToken) {
        mapStatus.textContent = 'The map is currently unavailable.';
        mapStatus.hidden = false;
        return;
    }
    if (!window.mapboxgl) {
        showMapError();
        return;
    }
    mapboxgl.accessToken = mapboxToken;
    try {
        map = new mapboxgl.Map({
            container: 'map',
            // Display overlays and the calculated route share one basemap.
            style: 'mapbox://styles/mapbox/light-v10',
            projection: 'mercator',
            center: [14.24641, 40.85631],
            zoom: 3,
            attributionControl: false
        });
    } catch (error) {
        showMapError();
        return;
    }
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.addControl(new mapboxgl.FullscreenControl({ container: document.documentElement }), 'top-right');
    map.addControl(new mapboxgl.ScaleControl({ maxWidth: 100, unit: 'nautical' }), 'bottom-right');
    map.addControl(new mapboxgl.AttributionControl({ compact: true }), 'bottom-right');
    map.on('error', showMapError);
    map.on('idle', () => { mapStatus.hidden = true; });

    function fitRoute() {
        if (!routeBounds) return;
        const rect = panel.getBoundingClientRect();
        const padding = compactScreen.matches
            ? { top: Math.min(rect.bottom + 28, window.innerHeight * .6), right: 55, bottom: 175, left: 35 }
            : { top: 65, right: 85, bottom: 175, left: rect.right + 55 };
        // Fit in the area beside the panel so the route remains unobstructed.
        map.fitBounds(routeBounds, { padding, maxZoom: 9, duration: 0 });
    }
    map.on('load', () => {
        mapStatus.hidden = true;
        if (map.getLayer('water')) map.setPaintProperty('water', 'fill-color', '#d8e6e1');
        if (map.getLayer('background')) map.setPaintProperty('background', 'background-color', '#f4f3ed');
        for (const layer of map.getStyle().layers) {
            if (layer.type === 'symbol' && layer.layout &&
                JSON.stringify(layer.layout['text-field'] || '').includes('name')) {
                map.setLayoutProperty(layer.id, 'text-field', ['coalesce', ['get', 'name_en'], ['get', 'name']]);
            }
        }
        const mapElement = document.getElementById('map');
        const overlays = window.MaritimeOverlays.mount(map, mapboxgl, {
            ports: mapElement.dataset.portsUrl,
            network: mapElement.dataset.networkUrl
        });
        const portsToggle = document.getElementById('show-ports');
        const networkToggle = document.getElementById('show-network');
        portsToggle.disabled = false;
        networkToggle.disabled = false;
        overlays.setPortsVisible(portsToggle.checked);
        overlays.setNetworkVisible(networkToggle.checked);
        portsToggle.addEventListener('change', () => overlays.setPortsVisible(portsToggle.checked));
        networkToggle.addEventListener('change', () => overlays.setNetworkVisible(networkToggle.checked));
        // Add the selected route last so it stays crisp above the context layers.
        if (routeCoordinates.length < 2) return;
        map.addSource('calculated-route', {
            type: 'geojson',
            data: {
                'type': 'Feature',
                'properties': {},
                'geometry': { 'type': 'LineString', 'coordinates': routeCoordinates }
            }
        });
        map.addLayer({
            id: 'route-outline', type: 'line', source: 'calculated-route',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: { 'line-color': '#ffffff', 'line-width': 7, 'line-opacity': .85 }
        });
        map.addLayer({
            id: 'route-layer', type: 'line', source: 'calculated-route',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: { 'line-color': '#1b6256', 'line-width': 3.5 }
        });
        [[routeCoordinates[0], 'A', 'Departure'], [routeCoordinates[routeCoordinates.length - 1], 'B', 'Destination']].forEach(([point, letter, label]) => {
            const marker = document.createElement('div');
            marker.className = 'route-marker' + (letter === 'B' ? ' arrival' : '');
            marker.textContent = letter;
            marker.setAttribute('role', 'img');
            marker.setAttribute('aria-label', label + ' network point');
            new mapboxgl.Marker({ element: marker }).setLngLat(point).addTo(map);
        });
        routeBounds = routeCoordinates.reduce(
            (bounds, point) => bounds.extend(point),
            new mapboxgl.LngLatBounds(routeCoordinates[0], routeCoordinates[0])
        );
        const fitButton = document.getElementById('fit-route');
        fitButton.hidden = false;
        fitButton.addEventListener('click', () => {
            if (compactScreen.matches) setPanelExpanded(false);
            fitRoute();
        });
        fitRoute();
    });
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (compactScreen.matches && routeBounds) setPanelExpanded(false);
            map.resize();
            fitRoute();
        }, 120);
    });
});
