// Native scrolling keeps the photographs accessible without a carousel runtime.
export function attachRailNavigation(rail, controls) {
  if (!rail || !controls) return () => {};
  const previous = controls.querySelector('[data-rail-previous]');
  const next = controls.querySelector('[data-rail-next]');
  const position = controls.querySelector('[data-rail-position]');
  let frame = 0;
  function measure() {
    const items = [...rail.children];
    const left = rail.getBoundingClientRect().left;
    const inset = parseFloat(getComputedStyle(rail).paddingLeft) || 0;
    const points = items.map(item => rail.scrollLeft + item.getBoundingClientRect().left - left - inset);
    const limit = Math.max(0, rail.scrollWidth - rail.clientWidth);
    let index = 0;
    for (let i = 1; i < points.length; i++) {
      if (Math.abs(points[i] - rail.scrollLeft) < Math.abs(points[index] - rail.scrollLeft)) index = i;
    }
    if (limit > 2 && rail.scrollLeft >= limit - 2) index = items.length - 1;
    return {points, limit, index};
  }
  function update() {
    frame = 0;
    const {points, limit, index} = measure();
    if(limit <= 2 && controls.contains(document.activeElement) && rail.getClientRects().length){
      const item=rail.children[index];
      (item?.matches('button,a[href]')?item:item?.querySelector('button,a[href]'))?.focus({preventScroll:true});
    }
    controls.hidden = limit <= 2;
    previous.setAttribute('aria-disabled',String(rail.scrollLeft <= 2));
    next.setAttribute('aria-disabled',String(rail.scrollLeft >= limit - 2));
    position.textContent = `${index + 1} / ${points.length}`;
  }
  function schedule() { if (!frame) frame = requestAnimationFrame(update); }
  function move(direction) {
    const {points, limit, index} = measure();
    if((direction < 0 && rail.scrollLeft <= 2)||(direction > 0 && rail.scrollLeft >= limit - 2))return;
    const target = Math.max(0, Math.min(points.length - 1, index + direction));
    rail.scrollTo({left: Math.min(limit, Math.max(0, points[target] || 0)),
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  }
  const back = () => move(-1), forward = () => move(1);
  previous.addEventListener('click', back);
  next.addEventListener('click', forward);
  rail.addEventListener('scroll', schedule, {passive:true});
  const observer = new ResizeObserver(schedule);
  observer.observe(rail);
  update();
  return () => {
    observer.disconnect(); cancelAnimationFrame(frame);
    previous.removeEventListener('click', back); next.removeEventListener('click', forward);
    rail.removeEventListener('scroll', schedule);
  };
}
