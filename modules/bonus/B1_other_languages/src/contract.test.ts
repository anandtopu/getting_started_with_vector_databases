import assert from "node:assert/strict";
import test from "node:test";
import {exactSearch, validateVector, type Listing} from "./contract.js";

test("shape, finite values and cosine zero guard", () => {
  for (const v of [[1], [NaN,0], [0,0]]) assert.throws(() => validateVector(v,2));
  validateVector([1,0],2);
});
test("scope before ranking and deterministic ties", () => {
  const rows: Listing[] = ["b","a","foreign"].map(id => ({id,uuid:id,vector:[1,0],seller_id:id==="foreign"?"other":"seller",title:id,price:1}));
  assert.deepEqual(exactSearch(rows,[1,0],"seller",10),["a","b"]);
  assert.deepEqual(exactSearch(rows,[1,0],"missing",10),[]);
  assert.throws(() => exactSearch(rows,[1,0],"",5));
});
