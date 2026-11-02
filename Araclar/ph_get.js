// Poly Haven (CC0) indirici: node ph_get.js <kök> models|textures id1,id2 [--res 2k]
const fs=require("fs"),path=require("path");
const [root,kind,ids]=process.argv.slice(2);const ri=process.argv.indexOf("--res");const RES=ri>0?process.argv[ri+1]:"2k";
const UA={"User-Agent":"Sisli-asset-fetch/1.0"};
const get=async u=>{for(let t=0;t<3;t++){try{const r=await fetch(u,{headers:UA});if(r.ok)return Buffer.from(await r.arrayBuffer());}catch(e){}await new Promise(r=>setTimeout(r,1500))}throw new Error("indirilemedi "+u)};
const save=async(u,p)=>{if(fs.existsSync(p)&&fs.statSync(p).size>0)return;fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,await get(u))};
(async()=>{for(const id of ids.split(",")){try{
 const files=JSON.parse((await get("https://api.polyhaven.com/files/"+id)).toString());const out=path.join(root,kind,id);
 if(kind==="models"){const g=files.gltf;const res=g[RES]?RES:Object.keys(g).sort()[0];const e=g[res].gltf;await save(e.url,path.join(out,path.basename(e.url)));for(const [rel,inc] of Object.entries(e.include||{}))await save(inc.url,path.join(out,rel));console.log("MODEL",id,res)}
 else{for(const mp of ["Diffuse","nor_gl","Rough","AO","arm","Displacement"]){if(!files[mp])continue;const res=files[mp][RES]?RES:Object.keys(files[mp]).sort()[0];const f=files[mp][res];const fmt=f.jpg?"jpg":(f.png?"png":Object.keys(f)[0]);await save(f[fmt].url,path.join(out,mp+"."+fmt))}console.log("DOKU",id)}
}catch(e){console.log("HATA",id,e.message)}}})();
