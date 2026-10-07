(() => {
    if (window.handyhelpersZoomCards) return;
    window.handyhelpersZoomCards=true;
    document.addEventListener('mouseover',event=>{
        const card=event.target.closest('.zoom-card'); if (!card || card.contains(event.relatedTarget)) return;
        card.classList.add('scale-up'); for (const sibling of card.parentElement.children) if (sibling!==card) sibling.classList.add('scale-down');
    });
    document.addEventListener('mouseout',event=>{
        const card=event.target.closest('.zoom-card'); if (!card || card.contains(event.relatedTarget)) return;
        card.classList.remove('scale-up'); for (const sibling of card.parentElement.children) sibling.classList.remove('scale-down');
    });
})();
