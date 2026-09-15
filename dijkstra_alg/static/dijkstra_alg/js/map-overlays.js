/* Port and shipping-lane display layers; independent of route calculation. */
(function (root) {
    'use strict';

    function portContent(feature) {
        const properties = feature.properties;
        const [longitude, latitude] = feature.geometry.coordinates;
        const content = document.createElement('section');
        content.className = 'port-card';
        content.setAttribute('aria-label', 'Port information');
        const eyebrow = document.createElement('p');
        eyebrow.className = 'eyebrow';
        eyebrow.textContent = 'Port information';
        const name = document.createElement('h2');
        // Dataset strings are text, never interpreted as markup.
        name.textContent = properties.name || 'Unnamed port';
        const country = document.createElement('p');
        country.className = 'port-country';
        country.textContent = properties.country || properties.country_code || 'Country not listed';
        const details = document.createElement('dl');
        const rows = [
            ['Port code', properties.code || 'Not listed'],
            ['Type', properties.port_type || 'Not listed'],
            ['Coordinates', `${latitude.toFixed(4)}°, ${longitude.toFixed(4)}°`]
        ];
        rows.forEach(([label, value]) => {
            const term = document.createElement('dt');
            const description = document.createElement('dd');
            term.textContent = label;
            description.textContent = value;
            details.append(term, description);
        });
        content.append(eyebrow, name, country, details);
        return content;
    }

    function mount(map, mapbox, urls) {
        map.addSource('shipping-network', { type: 'geojson', data: urls.network });
        map.addLayer({
            id: 'shipping-lanes', type: 'line', source: 'shipping-network',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: {
                'line-color': '#54877e',
                'line-width': ['interpolate', ['linear'], ['zoom'], 1, .8, 6, 1.35, 10, 1.8],
                'line-opacity': .2,
                'line-blur': 1.1
            }
        });
        map.addSource('port-catalogue', { type: 'geojson', data: urls.ports });
        map.addLayer({
            id: 'port-halos', type: 'circle', source: 'port-catalogue',
            paint: {
                'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, 4, 4, 8, 9, 12],
                'circle-color': '#c79047', 'circle-opacity': .19, 'circle-blur': .6
            }
        });
        map.addLayer({
            id: 'port-circles', type: 'circle', source: 'port-catalogue',
            paint: {
                'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, 2.3, 4, 4, 9, 6],
                'circle-color': ['case', ['boolean', ['feature-state', 'hover'], false], '#17574b', '#b9833e'],
                'circle-stroke-width': 1.25,
                'circle-stroke-color': '#fffef8',
                'circle-opacity': .94
            }
        });
        const popup = new mapbox.Popup({ closeButton: true, closeOnClick: false, offset: 14, maxWidth: '270px', className: 'port-popup' });
        let hoveredId = null;
        let pinned = false;
        let showing = false;

        function resetHighlight() {
            if (hoveredId !== null) map.setFeatureState({ source: 'port-catalogue', id: hoveredId }, { hover: false });
            hoveredId = null;
        }
        function clear() {
            pinned = false;
            showing = false;
            resetHighlight();
            popup.remove();
        }
        popup.on('close', () => {
            pinned = false;
            showing = false;
            resetHighlight();
        });
        function show(event, feature, pin) {
            if (!feature) return;
            const alreadyShowing = showing && hoveredId === feature.id;
            pinned = pin;
            if (alreadyShowing) return;
            resetHighlight();
            hoveredId = feature.id;
            map.setFeatureState({ source: 'port-catalogue', id: hoveredId }, { hover: true });
            const coordinates = feature.geometry.coordinates.slice();
            // Keep the popup beside the hovered world copy across the date line.
            while (Math.abs(event.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += event.lngLat.lng > coordinates[0] ? 360 : -360;
            }
            popup.setLngLat(coordinates).setDOMContent(portContent(feature));
            if (!popup.isOpen()) popup.addTo(map);
            pinned = pin;
            showing = true;
        }
        map.on('mousemove', 'port-circles', event => {
            map.getCanvas().style.cursor = 'pointer';
            if (!pinned) show(event, event.features[0], false);
        });
        map.on('mouseleave', 'port-circles', () => {
            map.getCanvas().style.cursor = '';
            if (!pinned) clear();
        });
        // Tapping/clicking pins a card; tapping elsewhere or its close button clears it.
        map.on('click', event => {
            const features = map.queryRenderedFeatures(event.point, { layers: ['port-circles'] });
            if (features.length) show(event, features[0], true);
            else clear();
        });
        return {
            setPortsVisible(visible) {
                clear();
                map.getCanvas().style.cursor = '';
                ['port-halos', 'port-circles'].forEach(layer => map.setLayoutProperty(layer, 'visibility', visible ? 'visible' : 'none'));
            },
            setNetworkVisible(visible) {
                map.setLayoutProperty('shipping-lanes', 'visibility', visible ? 'visible' : 'none');
            }
        };
    }
    root.MaritimeOverlays = { mount, portContent };
})(window);
