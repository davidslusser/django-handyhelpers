/* Chart configurations are JSON data, never interpolated JavaScript. */
(() => {
    window.initializeHandyhelpersCharts = (root=document) => {
        if (!window.Chart) return;
        const wrappers=[...(root.matches?.('[data-hh-chart]')?[root]:[]),...root.querySelectorAll('[data-hh-chart]')];
        const style=getComputedStyle(document.documentElement);
        const color = value => {
            if (Array.isArray(value)) return value.map(color);
            if (typeof value!=='string') return value;
            return style.getPropertyValue('--bs-'+value.replace(/^theme\./,'')).trim() || value;
        };
        for (const wrapper of wrappers) {
            const canvas=document.getElementById(wrapper.dataset.hhChart);
            if (!canvas || Chart.getChart(canvas)) continue;
            const configuration=JSON.parse(wrapper.querySelector('script[type="application/json"]').textContent);
            configuration.data.datasets.forEach(dataset=>{
                for (const name of ['backgroundColor','borderColor']) if (dataset[name]) dataset[name]=color(dataset[name]);
            });
            const chart=new Chart(canvas,configuration);
            canvas.onclick=event=>{
                const point=chart.getElementsAtEventForMode(event,'nearest',{intersect:true},true)[0];
                if (!point) return;
                const url=chart.data.datasets[point.datasetIndex].urls?.[point.index];
                if (url) {
                    const target=new URL(url,location.href);
                    if (['https:','http:'].includes(target.protocol)) location.href=target.href;
                }
            };
        }
    };
})();
