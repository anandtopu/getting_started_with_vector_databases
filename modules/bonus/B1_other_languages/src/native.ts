/** Run genuine frozen MiniLM vectors through either official TypeScript client. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {randomUUID} from "node:crypto";
import {performance} from "node:perf_hooks";
import {QdrantClient} from "@qdrant/js-client-rest";
import weaviate from "weaviate-client";
import {validateVector, type Fixture} from "./contract.js";

function loadFixture(): Fixture {
  try {
    const value = JSON.parse(readFileSync(process.env.MARLOWE_TS_FIXTURE ?? resolve(import.meta.dirname,"../../../../.cache/marlowe/bonus/ts-fixture.json"),"utf8")) as Fixture;
    assert.ok(value.records.length > 0, "Fixture must contain records");
    validateVector(value.query,value.dimensions);
    value.records.forEach(r => validateVector(r.vector,value.dimensions));
    return value;
  } catch (error) {
    console.error("Prepare the vector fixture with python scripts/prepare_bonus.py from the repository root.", String(error));
    process.exit(1);
  }
}
const fixture = loadFixture();
const seller = fixture.records[0]!.seller_id;
const first = fixture.records[0]!;
const start = performance.now();

async function qdrant(): Promise<object> {
  const client = new QdrantClient({url:process.env.MARLOWE_QDRANT_URL ?? "http://127.0.0.1:6333"});
  const name = "marlowe_ts_"+randomUUID().replaceAll("-", "");
  await client.createCollection(name,{vectors:{size:fixture.dimensions,distance:"Cosine"}});
  try {
    const points = fixture.records.map((r,i) => ({id:i+1,vector:r.vector,payload:{businessId:r.id,sellerId:r.seller_id,title:r.title,price:r.price}}));
    await client.upsert(name,{wait:true,points});
    await client.upsert(name,{wait:true,points:[{...points[0]!,payload:{...points[0]!.payload,title:"updated"}}]});
    assert.equal((await client.count(name,{exact:true})).count,fixture.records.length);
    const found = await client.query(name,{query:fixture.query,limit:5,filter:{must:[{key:"sellerId",match:{value:seller}}]},with_payload:true});
    assert.ok(found.points.length>0 && found.points.every(p => p.payload?.sellerId===seller));
    assert.equal((await client.retrieve(name,{ids:[1],with_payload:true}))[0]?.payload?.title,"updated");
    await client.delete(name,{wait:true,points:[1]});
    assert.equal((await client.retrieve(name,{ids:[1]})).length,0);
    return {engine:"qdrant",rows:fixture.records.length,ids:found.points.map(p=>p.payload?.businessId),scoped:true,replacement:true,deletion:true};
  } finally { await client.deleteCollection(name); }
}

async function runWeaviate(): Promise<object> {
  const client = await weaviate.connectToLocal({host:process.env.MARLOWE_WEAVIATE_HOST ?? "127.0.0.1",port:Number(process.env.MARLOWE_WEAVIATE_PORT ?? 8080),grpcPort:Number(process.env.MARLOWE_WEAVIATE_GRPC_PORT ?? 50051)});
  const name = "MarloweTs"+randomUUID().replaceAll("-", "");
  type Props = {businessId:string;sellerId:string;title:string;price:number};
  try {
    const collection = await client.collections.create<Props>({name,vectorizers:weaviate.configure.vectors.selfProvided(),properties:[{name:"businessId",dataType:"text",tokenization:"field"},{name:"sellerId",dataType:"text",tokenization:"field"},{name:"title",dataType:"text"},{name:"price",dataType:"number"}]});
    try {
      const objects=fixture.records.map(r=>({id:r.uuid,vectors:r.vector,properties:{businessId:r.id,sellerId:r.seller_id,title:r.title,price:r.price}}));
      const batch=await collection.data.insertMany(objects);
      assert.equal(batch.hasErrors,false);
      await collection.data.replace({...objects[0]!,properties:{...objects[0]!.properties,title:"updated"}});
      assert.equal((await collection.aggregate.overAll()).totalCount,fixture.records.length);
      const found=await collection.query.nearVector(fixture.query,{limit:5,filters:collection.filter.byProperty("sellerId").equal(seller),returnMetadata:["distance"]});
      assert.ok(found.objects.length>0 && found.objects.every(p=>p.properties.sellerId===seller));
      assert.equal((await collection.query.fetchObjectById(first.uuid))?.properties.title,"updated");
      await collection.data.deleteById(first.uuid);
      assert.equal(await collection.data.exists(first.uuid),false);
      return {engine:"weaviate",rows:fixture.records.length,ids:found.objects.map(p=>p.properties.businessId),scoped:true,replacement:true,deletion:true};
    } finally { await client.collections.delete(name); }
  } finally { await client.close(); }
}

async function main(): Promise<void> {
  const backend=process.argv[2];
  if (backend!=="qdrant" && backend!=="weaviate") throw new Error("Choose qdrant or weaviate");
  const result=backend==="qdrant"?await qdrant():await runWeaviate();
  console.log(JSON.stringify({...result,space:fixture.space,totalMilliseconds:performance.now()-start}));
}

main().catch(error=>{console.error("Native lesson failed. Check scripts/check_env.py and start the selected loopback database:",error.message);process.exitCode=1;});
