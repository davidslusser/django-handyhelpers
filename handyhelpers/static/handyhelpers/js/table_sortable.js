/* Each custom table owns its pagination and sort state. */
(() => {
    const initialized = new WeakSet();
    window.dataValueInt = (a,b) => numericValue(a)-numericValue(b);
    window.dataValueFloat = window.dataValueInt;
    function numericValue(html) {
        const documentValue=new DOMParser().parseFromString(String(html),'text/html');
        return Number(documentValue.querySelector('[data-value]')?.dataset.value ?? documentValue.body.textContent) || 0;
    }
    window.initializeTables = (root=document) => {
        const tables=[...(root.matches?.('.sortable-table-wrapper table')?[root]:[]),...root.querySelectorAll('.sortable-table-wrapper table')];
        for (const table of tables) {
            if (initialized.has(table) || table.matches('[data-toggle="table"]')) continue;
            const wrapper=table.closest('.sortable-table-wrapper'), body=table.tBodies[0];
            if (!wrapper || !body) continue;
            initialized.add(table);
            let rows=Array.from(body.rows), page=1, enabled=true, sortIndex=-1, ascending=true;
            const pageSize=Math.max(1,parseInt(wrapper.dataset.paginationSize,10)||12);
            const nav=wrapper.querySelector('.sortable-table-nav'), pagination=nav?.querySelector('.pagination');
            const render = () => {
                const pages=Math.max(1,Math.ceil(rows.length/pageSize)); page=Math.min(page,pages);
                body.replaceChildren(...(enabled?rows.slice((page-1)*pageSize,page*pageSize):rows));
                if (!nav || !pagination) return;
                nav.hidden=!enabled || pages===1; pagination.replaceChildren();
                for (let number=1;number<=pages;number++) {
                    const item=document.createElement('li'); item.className='page-item'+(number===page?' active':'');
                    const button=document.createElement('button'); button.type='button'; button.className='page-link'; button.textContent=number;
                    if (number===page) button.setAttribute('aria-current','page');
                    button.onclick=()=>{page=number;render();}; item.append(button); pagination.append(item);
                }
            };
            for (const header of table.querySelectorAll('th.sortable')) {
                header.tabIndex=0;
                const sort = () => {
                    const index=header.cellIndex; ascending=sortIndex===index?!ascending:true; sortIndex=index;
                    rows.sort((a,b)=>{
                        const left=a.cells[index]?.dataset.value ?? a.cells[index]?.textContent.trim() ?? '';
                        const right=b.cells[index]?.dataset.value ?? b.cells[index]?.textContent.trim() ?? '';
                        const result=left!=='' && right!=='' && Number.isFinite(Number(left)) && Number.isFinite(Number(right))?
                            Number(left)-Number(right):left.localeCompare(right);
                        return ascending?result:-result;
                    });
                    table.querySelectorAll('th.sortable').forEach(node=>node.removeAttribute('aria-sort'));
                    header.setAttribute('aria-sort',ascending?'ascending':'descending'); page=1;render();
                };
                header.addEventListener('click',sort);
                header.addEventListener('keydown',event=>{if (['Enter',' '].includes(event.key)) {event.preventDefault();sort();}});
            }
            wrapper.querySelector('.pagination-toggle')?.addEventListener('click',()=>{enabled=!enabled;render();});
            render();
        }
    };
})();
