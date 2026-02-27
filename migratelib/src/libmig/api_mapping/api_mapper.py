import json
from pathlib import Path

from sentence_transformers import SentenceTransformer, util

from libmig.lib_index.api_models import API
from libmig.lib_index.lib_index import LibIndex
from libmig.utils.cache import read_cache, write_cache


def api_description(api: API):
    return f"{api.qualified_name}({api.signature})\n\n{api.doc}"


class APIMapper:
    def __init__(self, source_lib: LibIndex, target_lib: LibIndex, map_private=False):
        self.source_lib = source_lib
        self.target_lib = target_lib
        self.map_private = map_private
        self._embedding_map = {}
        self._embedder = None

    def embed(self, api: API):
        if not self._embedder:
            self._embedder = SentenceTransformer('all-MiniLM-L6-v2')

        if api.id not in self._embedding_map:
            self._embedding_map[api.id] = self._embedder.encode(api_description(api))

        return self._embedding_map[api.id]

    def map(self, src_api: API) -> list[(API, float)]:
        src = self.source_lib
        tgt = self.target_lib
        cache_path = Path("api-mapping",
                          f"{src.module_name}-{src.module_version}__{tgt.module_name}-{tgt.module_version}",
                          f"{src_api.qualified_name}.json")
        mapping_dict: dict = read_cache(cache_path, "json")
        if mapping_dict:
            mapping = [(self.target_lib.get_api(qualified_name), sim) for qualified_name, sim in mapping_dict.items()]
        else:
            mapping = self._map_impl(src_api)
            mapping_dict = {api.qualified_name: sim for api, sim in mapping}
            write_cache(cache_path, mapping_dict, "json")

        return mapping

    def _map_impl(self, src_api: API):
        tgt = self.target_lib
        src_emb = self.embed(src_api)
        similarities = []
        max_similarity = -1
        target_apis = tgt.get_all_apis() if self.map_private else tgt.get_public_apis()
        for target_api in target_apis:
            tgt_emb = self.embed(target_api)
            similarity = util.pytorch_cos_sim(src_emb, tgt_emb).item()
            similarities.append((target_api, similarity))
            max_similarity = max(max_similarity, similarity)
        min_similarity = max_similarity * 0.95
        mapped = sorted([(api, sim) for api, sim in similarities if sim >= min_similarity], key=lambda x: -x[1])
        return mapped

    def map_all(self, src_apis: list[API]) -> set[API]:
        mappings = set()
        for src_api in src_apis:
            this_mappings = self.map(src_api)
            mappings.update(m for m, sim in this_mappings)

        return mappings
