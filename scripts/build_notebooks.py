"""Regenerate cleared notebooks from the canonical runnable lesson examples.

Run: uv run python scripts/build_notebooks.py
Needs base nbformat only. Does not execute code, download anything, or start a server.
"""

import argparse
import subprocess
import sys
import textwrap

import nbformat as nbf

from common.lesson_runtime import PACKAGES, requirements
from common.settings import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", help="Build a single module directory name")
    selected = parser.parse_args().module
    experiments = {
        "00": "from common.teaching import catalog\nproducts, _, _, _ = catalog(100)\nproducts[['id', 'title', 'price']].head()",
        "01": "from common.teaching import hand_features\nfrom tinyvec.exact import exact_knn\nids, matrix, query = hand_features()\n# Change the query coordinates and predict which product wins.\nquery[:] = [0.2, 1.0]\nexact_knn(matrix, query, ids, 3)",
        "02": "from dataclasses import replace\nfrom common.embeddings import EmbeddingSpec\nspec = EmbeddingSpec()\nprint(spec.space)\nprint(replace(spec, query_prefix='query: ').space)",
        "03": "from common.apps.search import open_catalog, search_saved\nstore, _, _ = open_catalog(limit=100)\ntry:\n    _, hits, _ = search_saved(store, expression={'op': 'lte', 'field': 'price', 'value': 30})\n    print([(h.id, h.metadata['price']) for h in hits])\nfinally:\n    store.close()",
        "04": "from common.bench.metrics import precision_at_k, reciprocal_rank\n# Move the relevant mug through the ranking.\nfound = ['chair', 'mug', 'lamp']\nprint(precision_at_k(found, {'mug': 3}, 3), reciprocal_rank(found, {'mug': 3}))",
    }
    experiments.update(
        {
            "05": "from common.index_lessons import trial\nprint(trial('lsh', bits=6, tables=2))",
            "06": "from common.index_lessons import trial\nprint(trial('ivf', nlist=8, nprobe=1))",
            "07": "from common.index_lessons import trial\nprint(trial('hnsw', M=4, efConstruction=20, efSearch=10))",
            "08": "from common.index_lessons import prefix_results\nprint(prefix_results()['64'])",
            "09": "from tinyvec.mmap import experiment\nimport tempfile\nfrom pathlib import Path\nwith tempfile.TemporaryDirectory() as tmp:\n    print(experiment(Path(tmp), 1024, 16, 128))",
            "10": "from tinyvec.hybrid import fuse\nprint(fuse([['sku-9','boot'], ['boot','lamp']], constant=20))",
        }
    )
    experiments.update(
        {
            "17": "from common.search.query_parser import parse_query\nprint(parse_query('chair at most $100 in stock'))\n# Change at most to under. Which boundary changes?",
            "18": "from common.apps.rag import chunk_article\nfrom common.settings import data_dir\nchunks=chunk_article(data_dir()/'help_center/help-000.md', words=15, overlap=4)\nprint([(c.id,c.passage_id) for c in chunks])",
            "19": "from common.apps.recommendations import mmr\nprint(mmr(['a','b','c'], [[1,0],[.99,.01],[0,1]], [1,0], 2, .2))\n# Change relevance to 1 and explain the second choice.",
            "20": "from common.apps.multimodal import weighted_fusion\nprint(weighted_fusion({'image':['a','b'],'text':['b','a']},{'image':.7,'text':.3}))",
        }
    )
    experiments.update(
        {
            "21": "from tinyvec.storage import VersionedRows\ns=VersionedRows()\ns.upsert('a',1)\ns.upsert('a',2)\nprint(s.live(),s.compact())",
            "22": "from common.ops.capacity import estimate\nprint(estimate(rows=10000000,dimensions=768,replicas=2))\n# Change precision, replicas and headroom separately.",
            "23": "from common.security.identity import Principal\np=Principal('reader','seller-a','reader')\nprint(p.permits('read'),p.permits('write'))",
        }
    )
    modules = [
        *sorted((ROOT / "modules").glob("[0-9][0-9]_*")),
        *sorted((ROOT / "modules/bonus").glob("B[1-4]_*")),
    ]
    experiments.update(
        {
            "B1": "from common.teaching import catalog\nimport json\n_,_,query,meta=catalog(100)\nprint(len(json.loads(json.dumps(query.tolist()))),meta['space'])",
            "B2": "from tinyvec.wal import WriteAheadLog\nfrom pathlib import Path\nimport tempfile\nwith tempfile.TemporaryDirectory() as d:\n    log=WriteAheadLog(Path(d)/'log.jsonl')\n    log.append('delete',['withdrawn'])\n    print(log.replay())",
            "B3": "import numpy as np\nscores=np.array([1.,.8,.6])\nprint(scores.mean(),len(scores))\n# Repeating these queries does not create new independent judgments.",
            "B4": "import numpy as np\nfrom tinyvec.rabitq import RaBitQ\nx=np.random.default_rng(1).normal(size=(50,16)).astype(np.float32)\nq=RaBitQ(x)\nprint(q.distances(x[0])[0],q.payload_bytes)",
        }
    )
    for module in modules:
        if selected and module.name != selected:
            continue
        cells = [
            nbf.v4.new_markdown_cell(
                f"# {module.name}: interactive lesson\n\nRead README.md first. Predict each outcome before executing. Code below is mirrored from the scripts; edit a copy to experiment. No model downloads or containers are started."
            ),
            nbf.v4.new_code_cell(
                "import os, sys\nfrom common.settings import ROOT\nos.chdir(ROOT)\nsys.argv = ['notebook']\nos.environ['HF_HUB_OFFLINE'] = '1'\nos.environ['ANONYMIZED_TELEMETRY'] = 'False'"
            ),
        ]
        for path in sorted((module / "examples").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            relative = path.relative_to(ROOT).as_posix()
            cells.append(
                nbf.v4.new_markdown_cell(
                    f"## {path.stem}\n\nSource: `{relative}`. What do you expect? Which assertion could catch a wrong implementation?"
                )
            )
            extras, profile = requirements(source)
            if extras or profile:
                tests = [
                    f"importlib.util.find_spec({PACKAGES[extra]!r}) is None" for extra in extras
                ]
                hint = " ".join("--extra " + extra for extra in extras)
                if profile:
                    tests.append(
                        f"{profile!r} not in os.environ.get('MARLOWE_NOTEBOOK_PROFILES','').split(',')"
                    )
                    hint += f"; start {profile} and include it in MARLOWE_NOTEBOOK_PROFILES"
                cells.append(
                    nbf.v4.new_code_cell(
                        f"import importlib.util\nif {' or '.join(tests)}:\n    print({('SKIP native comparison: ' + hint)!r})\nelse:\n"
                        + textwrap.indent(source, "    ")
                    )
                )
            else:
                cells.append(nbf.v4.new_code_cell(source))
        cells += [
            nbf.v4.new_markdown_cell(
                "## Change one thing\n\nExplain the result before and after changing the input. The code below is deliberately small enough to inspect."
            ),
            nbf.v4.new_code_cell(
                experiments.get(
                    module.name[:2],
                    f"from common.teaching import catalog\nrows, _, _, _=catalog(100)\nprint(rows.groupby('region').price.median())\n# Change the group or price threshold, then repeat the native comparison for {module.name}.",
                )
            ),
            nbf.v4.new_markdown_cell(
                "## Finish\n\nComplete Practice, Apply, Stretch, and the six-question quiz in README.md. No notebook output is committed. Preview `scripts/cleanup.py` before deleting generated course files."
            ),
        ]
        notebook = nbf.v4.new_notebook(
            cells=cells,
            metadata={
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
            },
        )
        for number, cell in enumerate(notebook.cells):
            cell.id = f"m{module.name[:2]}-{number:02d}"
        destination = module / "notebook.ipynb"
        nbf.write(notebook, destination)
        for arguments in (["check", "--fix"], ["format"]):
            subprocess.run([sys.executable, "-m", "ruff", *arguments, str(destination)], check=True)
        print(module.name)


if __name__ == "__main__":
    main()
