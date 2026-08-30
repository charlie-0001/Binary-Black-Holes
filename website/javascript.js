const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function reposition(popup, reference) 
{
    popup.style.display = "block";
    const rect = reference.getBoundingClientRect();
    const targetLeft = (rect.left + rect.width / 2) - (popup.offsetWidth / 2);
    const yOffset = 10

    popup.style.left = `${targetLeft + window.scrollX}px`;
    popup.style.top = `${rect.bottom + window.scrollY + yOffset}px`;
}

const hoverContainers = [...document.querySelectorAll('[data-hover-group="roadmap"]')];

hoverContainers.forEach(container => {
    const popup = document.createElement("div");
    popup.textContent = container.dataset.hoverInfo;
    popup.classList.add("popup-display");

    popup.style.position = "absolute";
    popup.style.justifyContent = 'center';
    popup.style.alignItems = 'center';
    popup.style.display = "none";
    popup.style.opacity = "0";
    popup.style.zIndex = "1000";

    document.body.appendChild(popup);

    container.addEventListener('mouseenter', async () => {
        reposition(popup, container);
        popup.style.display = 'block';
        for (let i = 0; i < 100; i++)
        {
            popup.style.opacity = i/100;
            await sleep(0.5);
        }
    });

    container.addEventListener('mouseleave', () => {
        popup.style.display = 'none';
    });
});