/* Dialog and English form feedback, independent of map services. */
(function (root) {
    'use strict';

    function clearFieldError(input) {
        const error = document.getElementById(input.id + '-errors');
        input.removeAttribute('aria-invalid');
        error.textContent = '';
        error.hidden = true;
    }
    function validateRouteForm(form) {
        let firstInvalid = null;
        for (const [name, label] of [['start', 'departure'], ['end', 'destination']]) {
            const input = form.elements.namedItem(name);
            clearFieldError(input);
            const value = input.value.trim();
            const message = !value ? `Enter a ${label} location.`
                : value.length > input.maxLength ? `Use ${input.maxLength} characters or fewer.` : '';
            if (message) {
                const error = document.getElementById(input.id + '-errors');
                error.textContent = message;
                error.hidden = false;
                input.setAttribute('aria-invalid', 'true');
                if (!firstInvalid) firstInvalid = input;
            }
        }
        if (firstInvalid) firstInvalid.focus();
        return !firstInvalid;
    }
    function initialize() {
        for (const name of ['start', 'end']) {
            const input = document.getElementById(name);
            input.addEventListener('input', () => clearFieldError(input));
        }
        const trigger = document.getElementById('open-project');
        const dialog = document.getElementById('project-dialog');
        const close = document.getElementById('close-project');
        trigger.hidden = false;
        trigger.addEventListener('click', () => {
            dialog.showModal();
            dialog.querySelector('.project-body').scrollTop = 0;
            trigger.setAttribute('aria-expanded', 'true');
        });
        close.addEventListener('click', () => dialog.close());
        dialog.addEventListener('click', event => {
            if (event.target === dialog) dialog.close();
        });
        // Native dialog handles Escape, focus trapping and the inert background.
        dialog.addEventListener('close', () => {
            trigger.setAttribute('aria-expanded', 'false');
            trigger.focus({ preventScroll: true });
        });
    }
    root.MaritimeInterface = { initialize, validateRouteForm };
})(window);
