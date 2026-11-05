/** Explicit vectors and stable identities are the cross-language contract. */
export type Listing = {id: string; uuid: string; vector: number[]; seller_id: string; title: string; price: number};
export type Fixture = {space: string; dimensions: number; records: Listing[]; query: number[]};

export function validateVector(vector: number[], dimensions: number): void {
  if (vector.length !== dimensions || vector.some(x => !Number.isFinite(x)) || vector.every(x => x === 0)) {
    throw new Error("Expected a finite, nonzero vector in the declared space");
  }
}

export function exactSearch(rows: Listing[], query: number[], seller: string, k: number): string[] {
  validateVector(query, query.length);
  if (!seller || !Number.isInteger(k) || k < 1) throw new Error("Trusted seller and positive k required");
  const norm = (v: number[]) => Math.sqrt(v.reduce((s, x) => s + x*x, 0));
  return rows.filter(r => r.seller_id === seller).map(r => {
    validateVector(r.vector, query.length);
    const score = r.vector.reduce((s,x,i) => s + x*query[i]!, 0)/(norm(r.vector)*norm(query));
    return {id:r.id,score};
  }).sort((a,b) => b.score-a.score || a.id.localeCompare(b.id)).slice(0,k).map(r => r.id);
}
