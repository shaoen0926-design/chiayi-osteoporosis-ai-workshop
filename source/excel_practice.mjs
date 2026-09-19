import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const root=decodeURIComponent(new URL('./',import.meta.url).pathname);
const dir=root+'outputs/excel-practice/';
await fs.mkdir(dir,{recursive:true});
const spec=JSON.parse(await fs.readFile(root+'spec.json','utf8'));
const rows=spec.prompts.MAT_D.trim().split('\n').map((r,i)=>r.split(',').map((x,j)=>i&&j>=2?Number(x):x));
const wb=Workbook.create();
function sheet(name,data,widths){
 const s=wb.worksheets.add(name);s.getRange('A1').write(data);
 const r=s.getUsedRange();r.format.font={name:'Helvetica Neue',size:12,color:'#243B35'};r.format.rowHeight=26;
 s.getRangeByIndexes(0,0,1,widths.length).format={fill:'#216253',font:{name:'Helvetica Neue',bold:true,color:'#FFFFFF',size:12},rowHeight:30};
 widths.forEach((w,i)=>s.getRangeByIndexes(0,i,data.length,1).format.columnWidth=w);
 s.showGridLines=false;s.freezePanes.freezeRows(1);return s;
}
sheet('使用說明',[
 ['項目','說明'],
 ['主題','用骨鬆簡報理解測驗，練習資料整理與簡報修改。'],
 ['資料來源','所有作答數據均為教學用虛構資料，非病人資料或研究結果。'],
 ['分析問題','哪些主題需要更清楚的說明？用各題答對率與作答数協助改稿。'],
 ['測驗統計','每列一題，包含有效作答數與答對數；各題分母不同。'],
 ['清理練習','獨立的故意含錯誤版本；不要與測驗統計相加。保留原值和修改理由。'],
 ['答案對照','題目、正解及簡報頁碼，供改稿時定位。'],
 ['第一題','讀取工作表與欄位，找出缺漏、重複、文字數字及超出範圍。'],
 ['第二題','保留原表，新增清理紀錄；以測驗統計表計算答對率並製作圖表。'],
 ['第三題','製作Dashboard與逐頁改稿建議，提供可下載xlsx並實際開啟驗收。'],
 ['解讀限制','答對次數不是人數；沒有前後配對或臨床結果，不能推論療效。'],
 ],[24,90]);
wb.worksheets.getItem('使用說明').getRange('B2:B11').format.wrapText=true;
wb.worksheets.getItem('使用說明').getRange('A2:B11').format.rowHeight=42;
const raw=sheet('測驗統計',rows,[18,22,22,22]);
raw.getRange('C2:D6').setNumberFormat('#,##0');
raw.tables.add('A1:D6',true,'QuizData');
const dirty=[['列號',...rows[0]],...rows.slice(1).map((r,i)=>[i+1,...r])];
dirty[2][2]=' 營養迷思 ';dirty[3][3]=null;dirty[4][4]='12';dirty[5][4]=25;
dirty.push([6,...rows[1]]);
const clean=sheet('清理練習',dirty,[12,18,22,22,22]);
clean.getRange('D2:E7').setNumberFormat('#,##0');
clean.tables.add('A1:E7',true,'CleaningData');
const answers=spec.prompts.MAT_H.trim().split('\n').map((row,i)=>row.split(',').map((v,j)=>i&&j===3?Number(v):v));
const key=sheet('答案對照',answers,[16,62,16,22]);
key.getRange('B2:B6').format.wrapText=true;key.getRange('A2:D6').format.rowHeight=42;
key.tables.add('A1:D6',true,'AnswerKey');
wb.recalculate();
const actual=raw.getRange('C2:D6').values;
if(actual.reduce((n,r)=>n+r[0],0)!==94 || actual.reduce((n,r)=>n+r[1],0)!==57) throw Error('Source totals mismatch');
console.log((await wb.inspect({kind:'table',range:'測驗統計!A1:D6',include:'values,formulas',tableMaxRows:6,tableMaxCols:4})).ndjson);
for(const [name,range] of [['使用說明','A1:B11'],['測驗統計','A1:D6'],['清理練習','A1:E7'],['答案對照','A1:D6']]){
 const image=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
 await fs.writeFile(dir+name+'.png',new Uint8Array(await image.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(dir+'數據處理練習.xlsx');
await fs.copyFile(dir+'數據處理練習.xlsx',root+'../數據處理練習.xlsx');
console.log('Workbook saved');
