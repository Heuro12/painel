// Detecta moeda pelo país do navegador
document.addEventListener("DOMContentLoaded", async () => {
    const selectMoeda = document.getElementById("moeda");

    try {
        const resp = await fetch("https://ipapi.co/json/");
        const data = await resp.json();

        let pais = data.country;
        let moeda = "USD";

        if (pais === "BR") moeda = "BRL";
        else if (pais === "AO") moeda = "AOA";
        else if (pais === "PT") moeda = "EUR";
        else moeda = "USD";

        selectMoeda.value = moeda;
    } catch (err) {
        console.log("Erro ao detectar localização:", err);
    }
});
