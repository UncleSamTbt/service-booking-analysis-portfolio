// Node built-in modules only. No browser or external service needed.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const folder=path.dirname(fileURLToPath(import.meta.url));
const source=fs.readFileSync(path.join(folder,'dashboard_metrics.js'),'utf8').replace(/\r\n/g,'\n');
const sandbox={};vm.createContext(sandbox);vm.runInContext(source,sandbox);
const {filterBookings,computeMetrics}=sandbox.PortfolioMetrics;
const html=fs.readFileSync(path.join(folder,'dashboard.html'),'utf8').replace(/\r\n/g,'\n');
const match=html.match(/<script id="portfolio-data" type="application\/json">([\s\S]*?)<\/script>/);
assert.ok(match,'Generated HTML must embed its own data');
const payload=JSON.parse(match[1]);
assert.ok(html.includes(source),'Generated HTML must embed the tested metrics source');
for(const script of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)){
 if(!script[0].startsWith('<script id="portfolio-data"'))new vm.Script(script[1]);
}
assert.ok(!/<script[^>]+src=|<link[^>]+href=|\bfetch\s*\(/i.test(html),'Dashboard must have no external dependency');
const cases=JSON.parse(fs.readFileSync(path.join(folder,'metrics-baseline.json'),'utf8'));
let passed=0;
for(const test of cases){
 const actual=computeMetrics(filterBookings(payload.records,test.filters));
 for(const [key,expected]of Object.entries(test.metrics)){
  if(expected===null)assert.equal(actual[key],null,`${test.name}.${key}`);
  else assert.ok(Math.abs(actual[key]-expected)<0.00001,`${test.name}.${key}: ${actual[key]} != ${expected}`);
 }
 passed++;
}
const fixture=[
 {status:'completed',paid_amount_cents:10000,lead_days:2,actual_minutes:30,satisfaction_score:4},
 {status:'completed',paid_amount_cents:5000,lead_days:4,actual_minutes:60,satisfaction_score:5},
 {status:'cancelled',paid_amount_cents:0,lead_days:3,actual_minutes:null,satisfaction_score:null},
 {status:'no_show',paid_amount_cents:0,lead_days:7,actual_minutes:null,satisfaction_score:null},
 {status:'scheduled',paid_amount_cents:0,lead_days:2,actual_minutes:null,satisfaction_score:null}];
const m=computeMetrics(fixture);
assert.equal(m.collected_revenue_cents,15000);assert.equal(m.completion_rate_pct,50);
assert.equal(m.cancellation_rate_pct,25);assert.equal(m.mean_lead_days,3.6);
assert.equal(m.average_service_minutes,45);assert.equal(m.average_feedback_score,4.5);
assert.equal(m.resolved_count,4);assert.equal(m.booking_count,5);
assert.equal(computeMetrics([]).completion_rate_pct,null);
assert.equal(computeMetrics([fixture[4]]).cancellation_rate_pct,null);
const total=computeMetrics(payload.records);
const serviceTotals=['CLEAN','REPAIR','GARDEN'].map(service_code=>computeMetrics(filterBookings(payload.records,{service_code})));
assert.equal(serviceTotals.reduce((n,row)=>n+row.collected_revenue_cents,0),total.collected_revenue_cents);
assert.equal(serviceTotals.reduce((n,row)=>n+row.booking_count,0),total.booking_count);
assert.equal(payload.records.length,144);
assert.equal(total.completed_count,93);assert.equal(total.cancelled_count,26);
assert.equal(total.no_show_count,13);assert.equal(total.scheduled_count,12);
console.log(`PASS: ${passed} Python baseline selections, manual fixture, empty/scheduled denominators, service reconciliation, embedded source/data and standalone dependency check.`);
