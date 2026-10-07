(() => {
    document.querySelector('#sidebar-toggle')?.addEventListener('click',()=>document.querySelector('#sidebar')?.classList.toggle('collapsed'));
    const root=document.documentElement;
    try { if (localStorage.getItem('handyhelpers-theme')) root.dataset.bsTheme=localStorage.getItem('handyhelpers-theme'); } catch { /* Storage may be disabled. */ }
    document.querySelector('.theme-toggle')?.addEventListener('click',()=>{
        root.dataset.bsTheme=root.dataset.bsTheme==='dark'?'light':'dark';
        try {localStorage.setItem('handyhelpers-theme',root.dataset.bsTheme);} catch { /* Optional persistence. */ }
    });
})();
