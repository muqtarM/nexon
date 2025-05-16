(function(){
  const ws=new WebSocket(`${location.origin.replace('http','ws')}/notifications/ws`);
  ws.onmessage=e=>{
    const {title,message,level}=JSON.parse(e.data);
    toast(title,message,level);
  };
  function toast(t,m,l){
    const c=document.getElementById('toast-c')||createC();
    const d=document.createElement('div');
    d.className=`toast toast-${l}`;
    d.innerHTML=`<strong>${t}</strong><p>${m}</p>`;
    c.appendChild(d);
    setTimeout(()=>d.remove(),5000);
  }
  function createC(){
    const c=document.createElement('div');
    c.id='toast-c';c.style='position:fixed;top:1rem;right:1rem;z-index:9999;';
    document.body.appendChild(c);return c;
  }
})();
