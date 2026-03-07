import json

from ..db.nova_db import NovaDB


class CoreMemoryRepository:
    dbn = NovaDB()

    @classmethod
    def get_memories(cls, roles: list[str]=['user', 'agent']) -> dict:
        sql = f'''
SELECT id, role, key, value FROM core_memories
WHERE role in ?
      AND deleted = 0
ORDER BY role, id;
'''
        params = (roles,)
        return cls.dbn.execute_sql(sql, params, returns_data=True)

    @classmethod
    def add_memory(cls, role: str, key: str, value: str) -> dict:
        sql = f'''
INSERT INTO core_memories (role, key, value)
VALUES (?, ?, ?)
ON CONFLICT(role, key)
DO UPDATE SET
    value = excluded.value,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now');
'''
        params = (role, key, value)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def delete(cls, id: int) -> dict:
        sql = f'''
UPDATE core_memories
SET deleted = 1
WHERE id = ?;
'''
        params = (id,)
        return cls.dbn.execute_sql(sql, params)
    
    @classmethod
    def undelete(cls, id: int) -> dict:
        sql = f'''
UPDATE core_memories
SET deleted = 0
WHERE id = ?;
'''
        params = (id,)
        return cls.dbn.execute_sql(sql, params)
    
    