const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../../dijkstra_alg/static/dijkstra_alg/js/map-overlays.js'), 'utf8');
const port = (id = 2, name = 'Sample port') => ({
    id, properties: { name, country: '', country_code: 'USA', code: '', port_type: 'Sea' },
    geometry: { type: 'Point', coordinates: [0, 0] }
});

function setup() {
    const popups = [];
    class Popup {
        constructor() { this.open = false; this.handlers = {}; popups.push(this); }
        on(event, handler) { this.handlers[event] = handler; return this; }
        setLngLat(value) { this.coordinates = value; return this; }
        setDOMContent(value) { this.content = value; return this; }
        addTo() { this.remove(); this.open = true; return this; }
        isOpen() { return this.open; }
        remove() {
            const wasOpen = this.open;
            this.open = false;
            if (wasOpen && this.handlers.close) this.handlers.close();
            return this;
        }
    }
    const events = {}, layers = [], sources = {}, states = [];
    const canvas = { style: {} };
    const map = {
        rendered: [],
        addSource(id, source) { sources[id] = source; },
        addLayer(layer) { layers.push(layer); },
        on(event, layerOrHandler, handler) {
            events[handler ? event + ':' + layerOrHandler : event] = handler || layerOrHandler;
        },
        getCanvas() { return canvas; },
        setFeatureState(feature, state) { states.push({ id: feature.id, hover: state.hover }); },
        queryRenderedFeatures() { return this.rendered; },
        setLayoutProperty(id, property, value) {
            const layer = layers.find(item => item.id === id);
            layer.layout = { ...layer.layout, [property]: value };
        }
    };
    const document = {
        createElement(tag) {
            return { tag, children: [], attributes: {}, append(...items) { this.children.push(...items); },
                setAttribute(name, value) { this.attributes[name] = value; } };
        }
    };
    const context = { window: {}, document };
    vm.runInNewContext(source, context);
    const overlay = context.window.MaritimeOverlays.mount(map, { Popup }, { ports: '/ports', network: '/network' });
    const event = feature => ({ features: [feature], point: { x: 10, y: 10 }, lngLat: { lng: 0 } });
    return { overlay, events, layers, sources, states, map, popup: popups[0], event, canvas };
}

test('hover opens basic port information and leave clears the highlight', () => {
    const s = setup();
    s.events['mousemove:port-circles'](s.event(port()));
    assert.equal(s.popup.open, true);
    assert.equal(s.popup.content.children[1].textContent, 'Sample port');
    assert.equal(s.popup.content.children[2].textContent, 'USA');
    const details = s.popup.content.children[3].children;
    assert.equal(details[1].textContent, 'Not listed');
    assert.equal(details[5].textContent, '0.0000°, 0.0000°');
    s.events['mouseleave:port-circles']();
    assert.equal(s.popup.open, false);
    assert.equal(s.states.at(-1).hover, false);
    assert.equal(s.canvas.style.cursor, '');
});

test('moving between adjacent ports updates content and keeps the new highlight', () => {
    const s = setup();
    s.events['mousemove:port-circles'](s.event(port(2, 'First')));
    s.events['mousemove:port-circles'](s.event(port(3, 'Second')));
    assert.equal(s.popup.content.children[1].textContent, 'Second');
    assert.deepEqual(s.states.at(-1), { id: 3, hover: true });
    assert.equal(s.popup.open, true);
});

test('click or tap pins the selected port until the map or close button is clicked', () => {
    const s = setup();
    s.map.rendered = [port()];
    s.events.click(s.event(port()));
    s.events['mouseleave:port-circles']();
    assert.equal(s.popup.open, true);
    s.events['mousemove:port-circles'](s.event(port(3, 'Another port')));
    assert.equal(s.popup.content.children[1].textContent, 'Sample port');
    s.map.rendered = [];
    s.events.click(s.event(port()));
    assert.equal(s.popup.open, false);
    s.map.rendered = [port()];
    s.events.click(s.event(port()));
    s.popup.remove();
    assert.equal(s.states.at(-1).hover, false);
});

test('hiding ports dismisses the popup without affecting lanes or the selected route', () => {
    const s = setup();
    s.map.rendered = [port()];
    s.events.click(s.event(port()));
    s.overlay.setPortsVisible(false);
    assert.equal(s.popup.open, false);
    assert.equal(s.layers.find(l => l.id === 'port-circles').layout.visibility, 'none');
    assert.equal(s.layers.find(l => l.id === 'port-halos').layout.visibility, 'none');
    s.overlay.setNetworkVisible(false);
    assert.equal(s.layers.find(l => l.id === 'shipping-lanes').layout.visibility, 'none');
    s.overlay.setPortsVisible(true);
    assert.equal(s.layers.find(l => l.id === 'port-circles').layout.visibility, 'visible');
    assert.equal(s.layers.find(l => l.id === 'shipping-lanes').layout.visibility, 'none');
});

test('untrusted catalogue names are inserted as text rather than HTML', () => {
    const s = setup();
    const name = '<img src=x onerror=alert(1)>';
    s.events['mousemove:port-circles'](s.event(port(2, name)));
    assert.equal(s.popup.content.children[1].textContent, name);
    assert.equal(s.popup.content.children[1].innerHTML, undefined);
});

test('popup coordinates follow the displayed world copy without mutating the port', () => {
    const s = setup();
    const feature = port();
    feature.geometry.coordinates = [-179, 10];
    const event = s.event(feature);
    event.lngLat.lng = 181;
    s.events['mousemove:port-circles'](event);
    assert.equal(s.popup.coordinates[0], 181);
    assert.equal(feature.geometry.coordinates[0], -179);
});
