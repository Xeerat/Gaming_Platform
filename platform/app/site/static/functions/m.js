

// ------------------------------------
// Сохранение
// ------------------------------------
document.getElementById('saveBtn').addEventListener('click', async ()=>{
    const name=prompt("Введите название карты (1-10 символов):");
    if(!name||name.length<1||name.length>10){ alert("Имя 1–10 символов"); return; }
    const payload={ map_name:name, matrix:mapMatrix };
    try{
        const resp=await fetch("http://localhost:8000/map/add_map/",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            credentials:"include",
            body:JSON.stringify(payload)
        });
        if(!resp.ok){ const data=await resp.json(); alert("Ошибка: "+(data.detail||"неизвестная")); return;}
        alert("Карта сохранена!");
    }catch(e){console.error(e); alert("Ошибка сети");}
});
