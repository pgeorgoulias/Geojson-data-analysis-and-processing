const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../../dijkstra_alg/static/dijkstra_alg/js/interface.js'), 'utf8');

function setup(start = '', end = '') {
    const fields = {};
    let focused;
    for (const [id, value] of [['start', start], ['end', end]]) {
        fields[id] = { id, value, maxLength: 100, attributes: {},
            setAttribute(key, value) { this.attributes[key] = value; },
            removeAttribute(key) { delete this.attributes[key]; },
            focus() { focused = id; } };
        fields[id + '-errors'] = { textContent: '', hidden: true };
    }
    const context = { window: {}, document: { getElementById: id => fields[id] } };
    vm.runInNewContext(source, context);
    return { api: context.window.MaritimeInterface, fields, form: { elements: { namedItem: name => fields[name] } }, focused: () => focused };
}

test('empty and whitespace-only fields show English messages and focus departure', () => {
    const s = setup('  ', '');
    assert.equal(s.api.validateRouteForm(s.form), false);
    assert.equal(s.fields['start-errors'].textContent, 'Enter a departure location.');
    assert.equal(s.fields['end-errors'].textContent, 'Enter a destination location.');
    assert.equal(s.fields.start.attributes['aria-invalid'], 'true');
    assert.equal(s.focused(), 'start');
});

test('corrected values clear old errors and allow the existing form submission', () => {
    const s = setup();
    s.api.validateRouteForm(s.form);
    s.fields.start.value = 'Piraeus';
    s.fields.end.value = 'Rotterdam';
    assert.equal(s.api.validateRouteForm(s.form), true);
    assert.equal(s.fields['start-errors'].hidden, true);
    assert.equal(s.fields['end-errors'].textContent, '');
    assert.equal(s.fields.start.attributes['aria-invalid'], undefined);
    assert.equal(s.fields.start.value, 'Piraeus');
});

test('overlong destinations are rejected in English and focus that field', () => {
    const s = setup('Piraeus', 'x'.repeat(101));
    assert.equal(s.api.validateRouteForm(s.form), false);
    assert.equal(s.fields['end-errors'].textContent, 'Use 100 characters or fewer.');
    assert.equal(s.focused(), 'end');
});
