function reposition(newPopup, reference) {
    const rect = reference.getBoundingClientRect();
    
    const centerX = rect.left + rect.width / 2 + window.scrollX;
    const bottomY = rect.bottom + window.scrollY + 8;

    newPopup.style.left = `${centerX}px`;
    newPopup.style.top = `${bottomY}px`;
    newPopup.style.transform = 'translateX(-50%)';
}

const hoverContainers = [...document.querySelectorAll('[data-hover-group="roadmap"]')];

hoverContainers.forEach(container => {
    const popup = document.createElement("div");
    popup.textContent = `Popup for #${container.id}`;
    popup.classList.add("popup-display");

    popup.style.position = "absolute";
    popup.style.display = "none";
    popup.style.zIndex = "1000";

    document.body.appendChild(popup);

    container.addEventListener('mouseenter', () => {
        reposition(popup, container);
        popup.style.display = 'block';
    });

    container.addEventListener('mouseleave', () => {
        popup.style.display = 'none';
    });
});