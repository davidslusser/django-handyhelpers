/* Bootstrap and HTMX lifecycle integration. Ordinary messages/titles are text. */
(() => {
    if (window.initializeHandyhelpers) return;
    const instances = new WeakSet();
    const elements = (root, selector) => root?.querySelectorAll ?
        [ ...(root.matches?.(selector) ? [root] : []), ...root.querySelectorAll(selector) ] : [];
    function initialize(root = document) {
        if (window.bootstrap) {
            for (const element of elements(root, '[data-bs-toggle="tooltip"]')) bootstrap.Tooltip.getOrCreateInstance(element);
            for (const element of elements(root, '[data-bs-toggle="popover"]')) bootstrap.Popover.getOrCreateInstance(element);
        }
        if (window.jQuery?.fn.bootstrapTable) {
            for (const table of elements(root, '[data-toggle="table"]')) {
                if (!instances.has(table)) { jQuery(table).bootstrapTable(); instances.add(table); }
            }
        }
        if (window.ClipboardJS && !window.handyhelpersClipboard) window.handyhelpersClipboard = new ClipboardJS('.cpy');
        window.initializeTables?.(root);
        window.initializeHandyhelpersCharts?.(root);
    }
    window.initializeHandyhelpers = initialize;
    window.getCookie = name => document.cookie.split(';').map(part => part.trim()).find(part => part.startsWith(name+'='))?.slice(name.length+1) || '';
    window.csrfSafeMethod = method => /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    window.showModal = id => bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).show();
    window.hideModal = id => bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).hide();
    window.toggleModal = id => bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).toggle();
    window.doPost = url => { const form = document.getElementById('modalsubmitform'); form.action=url; form.method='POST'; form.requestSubmit(); };
    window.confirmAction = (url, title='Confirm', confirmation='Do you wish to continue?', button='Continue', method='GET') => {
        if (!url) return;
        document.getElementById('id_modalConfirmHeader').textContent=title;
        document.getElementById('id_modalConfirmBody').textContent=confirmation;
        const ok = document.getElementById('id_modalConfirm_OK');
        ok.textContent=button; ok.removeAttribute('href'); ok.onclick=null;
        if (method==='POST') ok.onclick=event => { event.preventDefault(); doPost(url); };
        else ok.href=url;
        showModal('id_modalConfirm');
    };
    function showContent(title, html, large=false) {
        const suffix=large==='xl'?'ExtraLarge':large?'Large':'';
        document.getElementById('id_modalResults'+suffix+'Header').textContent=title;
        document.getElementById('id_modalResults'+suffix+'Body').innerHTML=html;
        showModal('id_modalResults'+suffix);
    }
    window.showLocalInfo = (title, html, large=false) => showContent(title, html, large);
    window.showObjectInfo = window.showLocalInfo;
    window.showInfo = async (url, id, title='Show Info', large=false) => {
        const target=new URL(url, location.href); target.searchParams.set('client_response', id);
        const response=await fetch(target, {headers:{'X-Requested-With':'XMLHttpRequest'}});
        if (!response.ok) throw new Error('Request failed: '+response.status);
        showContent(title,(await response.json()).server_response,large);
        return false;
    };
    window.showImage = (id, title='', link, linkLabel) => {
        document.getElementById('id_modalImageHeader').textContent=title;
        document.querySelector('.modal_image').src=document.getElementById(id).src;
        if (link) document.getElementById('id_image_link').href=link;
        if (linkLabel) document.getElementById('id_image_link_label').textContent=linkLabel;
        showModal('id_modalImage');
    };
    window.showToast = message => {
        const container=document.querySelector('.toast-container');
        if (!container || !window.bootstrap) return;
        const toast=document.createElement('div'); toast.className='toast'; toast.setAttribute('role','status');
        const body=document.createElement('div'); body.className='toast-body'; body.textContent=message; toast.append(body);
        container.append(toast);
        toast.addEventListener('hidden.bs.toast',()=>{ bootstrap.Toast.getInstance(toast)?.dispose(); toast.remove(); },{once:true});
        bootstrap.Toast.getOrCreateInstance(toast).show();
    };
    document.addEventListener('DOMContentLoaded', () => {
        initialize(document);
        Promise.all(Object.values(window.handyhelpersAssets || {})).then(()=>initialize(document));
    });
    document.addEventListener('htmx:afterSwap', event => initialize(event.detail.target));
    document.addEventListener('htmx:beforeSwap', event => {
        if (event.detail.xhr.status===422) { event.detail.shouldSwap=true; event.detail.isError=false; }
    });
    document.addEventListener('htmx:configRequest', event => {
        if (!csrfSafeMethod(event.detail.verb.toUpperCase())) {
            const token=event.detail.elt.closest('form')?.querySelector('[name="csrfmiddlewaretoken"]')?.value || getCookie('csrftoken');
            event.detail.headers['X-CSRFToken']=token;
        }
    });
    document.addEventListener('htmx:afterRequest', event => {
        const message=event.detail.xhr.getResponseHeader('X-Toast-Message');
        if (message) showToast(message);
        if (event.detail.successful && event.detail.elt.closest('#modal_wrapper') && event.detail.target.id==='body_main') hideModal('modal_wrapper');
    });
    document.addEventListener('handyhelpers:created', event => { hideModal('modal_wrapper'); showToast(event.detail.message); });
    document.addEventListener('hidden.bs.modal', event => {
        if (event.target.id==='modal_wrapper') event.target.replaceChildren();
    });
    document.addEventListener('htmx:beforeCleanupElement', event => {
        const root=event.detail.elt;
        for (const node of elements(root,'[data-bs-toggle="tooltip"], [data-bs-toggle="popover"]')) {
            bootstrap.Tooltip.getInstance(node)?.dispose(); bootstrap.Popover.getInstance(node)?.dispose();
        }
        for (const canvas of elements(root,'canvas')) window.Chart?.getChart(canvas)?.destroy();
    });
})();
