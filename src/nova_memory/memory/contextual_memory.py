from dataclasses import dataclass, field, replace
from typing import Dict
import json


from .._db.repositories.contextual_memory_repo import ContextualMemoryRepository


@dataclass
class Memory:
    text: str
    metadata: Dict = field(default_factory=dict)
    kind: str = 'note'
    token_count: int = len(text.split())
    

class ContextualMemory:
    def __init__(self, max_chunk: int=400, overlap: int=50):
        self.max_chunk = max_chunk
        self.overlap = overlap
        self._contextual_memory_repo = ContextualMemoryRepository
       
    def add_memory(self, memory: Memory | tuple[Memory, ...], preprocessed: bool=False) -> None:
        memories = memory if isinstance(memory, tuple) else (memory,)
        if not all(isinstance(item, Memory) for item in memories):
            raise TypeError('Memory items need to be instance of the Memory class')
        
        if not preprocessed:
            memories = self._process(memories, preprocessed)
        
        for item in memories:
            result = self._contextual_memory_repo.add_memory(
                item.text, 
                kind=item.kind, 
                meta=item.metadata
            )
            if result['error'] is not None:
                raise Exception(result['error'])
    
    def query_memories(self, query: str, k: int = 5, kind: str = 'note') -> list[Memory]:
        result = self._contextual_memory_repo.retrieve_memories(
            query, k=k, kind=kind
        )

        if result['error'] is not None:
            raise Exception(result['error'])

        return [
            Memory(
                text=item['m.text'],
                kind=item['m.kind'],
                metadata=json.loads(item['m.meta_json'])
            )
            for item in result['data']
        ]
        
    def _process(self, memories: tuple[Memory, ...]) -> list[Memory]:
        chunks = []
        
        for item in memories:
            if item.token_count > self.max_chunk:
                chunks.extend(self._chunk(item))
            else:
                chunks.append(item)
        
        return chunks

    def _chunk(self, item: Memory) -> list[Memory]:
        if self.token_len(item.text) <= self.max_tokens:
            return [item]

        chunks: list[Memory] = []

        paragraphs = [p.strip() for p in item.text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [item.text.strip()]

        for para in paragraphs:
            if self.token_len(para) <= self.max_tokens:
                chunks.append(replace(item, text=para))
            else:
                words = para.split()
                start = 0
                step = self.max_tokens - self.overlap_tokens

                while start < len(words):
                    piece = " ".join(words[start:start + self.max_tokens])
                    chunks.append(replace(item, text=piece))
                    start += max(step, 1)

        return chunks
                
            
        
        
        
        
        
        
    
    
        