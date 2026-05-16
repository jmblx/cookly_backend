import { setupPagination } from "./paginator.js";
import { renderCards } from "./renderers.js";

document.addEventListener("DOMContentLoaded", () => {
    setupPagination({
        containerId: "rs-container",
        fetchUrl: "/api/rs/ids_data",
        renderFn: renderCards,
        itemLinkBase: "/pages/resourceServer.html",
        queryParam: "rsId"
    });
});
