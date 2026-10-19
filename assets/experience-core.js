// Values come from the manufacturer's actual unit dimensions and pixel resolutions.
export function sizeScreen(option,width,height,fit='at-least'){
 if(!option||![width,height].every(Number.isFinite)||width<.1||width>30||height<.1||height>20||!['at-least','at-most'].includes(fit))throw new Error('En için 0,1–30 m, boy için 0,1–20 m arasında bir değer girin.');
 if(![option.width,option.height,option.pixelsX,option.pixelsY].every(v=>Number.isFinite(v)&&v>0))throw new Error('Bu ürünün ölçü bilgileri doğrulanamadı.');
 const round=value=>fit==='at-least'?Math.ceil(value-1e-9):Math.floor(value+1e-9);
 const columns=round(width*1000/option.width),rows=round(height*1000/option.height);
 if(columns<1||rows<1)throw new Error('Seçilen ürün hedef alana sığmıyor. Ölçüyü büyütün veya farklı bir ürün seçin.');
 return {columns,rows,total:columns*rows,width:columns*option.width/1000,height:rows*option.height/1000,pixelsX:columns*option.pixelsX,pixelsY:rows*option.pixelsY,area:columns*rows*option.width*option.height/1e6};
}
export function comparisonRows(products,onlyDifferences=false){
 const fields=[['Kullanım ortamı','environment'],['Piksel aralığı (mm)','pitch'],['Ünite ölçüsü','dimensions'],['Ünite çözünürlüğü','resolution'],['Parlaklık','luminance'],['Yenileme hızı','refresh'],['Servis yönü','maintenance'],['Koruma sınıfı','ip'],['Ort. güç / m² (föy)','averagePower'],['Azami güç / m² (föy)','maxPower']];
 return fields.map(([label,key])=>({label,values:products.map(p=>String(p[key]??'Belirtilmedi')+(['averagePower','maxPower'].includes(key)?' W/m²':''))})).filter(row=>!onlyDifferences||new Set(row.values).size>1);
}
