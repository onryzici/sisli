// görüntü parlaklık istatistiği: node parlaklik.js <png...>
const {execSync}=require("child_process");
for(const f of process.argv.slice(2)){
 const b=execSync(`ffmpeg -v error -i "${f}" -vf scale=160:90 -f rawvideo -pix_fmt rgb24 -`,{maxBuffer:1e8});
 let s=[0,0,0],L=[];for(let i=0;i<b.length;i+=3){s[0]+=b[i];s[1]+=b[i+1];s[2]+=b[i+2];L.push(0.2126*b[i]+0.7152*b[i+1]+0.0722*b[i+2]);}
 const n=b.length/3;L.sort((a,b)=>a-b);const p=q=>L[Math.floor(q*(L.length-1))].toFixed(0);
 console.log(f.split(/[\/]/).pop().padEnd(28),"ort RGB",s.map(v=>(v/n).toFixed(0)).join(","),"L p5/50/95/99.5",p(.05),p(.5),p(.95),p(.995));}
