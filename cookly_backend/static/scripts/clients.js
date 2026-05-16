import { setupPagination } from "./paginator.js";
import { renderCards } from "./renderers.js";

document.addEventListener("DOMContentLoaded", () => {
    setupPagination({
        containerId: "clients-container",
        fetchUrl: "/api/client/ids_data",
        renderFn: renderCards,
        itemLinkBase: "/pages/client.html",
        queryParam: "clientId"
    });
});
