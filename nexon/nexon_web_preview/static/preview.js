(async function(){
  const token = localStorage.getItem("preview_token") || prompt("API token:");
  if(token) localStorage.setItem("preview_token", token);
  const headers = { "Authorization": `Bearer ${token}` };

  async function fetchAndRender(path, container, formatter){
    const resp = await fetch(`/preview/${path}`, { headers });
    if(!resp.ok) return alert(`Error loading ${path}: ${resp.status}`);
    const data = await resp.json();
    formatter(container, data);
  }

  fetchAndRender("envs", document.querySelector("#envs ul"), (ul,envs)=>{
    ul.innerHTML = envs.map(e=>`<li>${e.name} (${e.role})</li>`).join("");
  });
  fetchAndRender("packages", document.querySelector("#pkgs ul"), (ul,pkgs)=>{
    ul.innerHTML = pkgs.map(p=>`<li>${p.name}-${p.version}</li>`).join("");
  });
  fetchAndRender("graph?env=dev", document.querySelector("#graph pre"), (pre,graph)=>{
    pre.textContent = JSON.stringify(graph, null, 2);
  });
})();
