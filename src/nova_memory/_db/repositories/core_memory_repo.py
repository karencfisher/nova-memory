import json

from ..db.nova_db import NovaDB


class CoreMemoryRepository:
    dbn = NovaDB()

    @classmethod
    def get_memories(cls, roles: list[str]=['user', 'agent']) -> dict:
        sql = f'''
SELECT id, role, key, value FROM core_memories
WHERE role in {roles}
      AND deleted = 0
ORDER BY role, id;
'''
        return cls.dbn.execute_sql(sql, returns_data=True)

    @classmethod
    def add_memory(cls, memory: str) -> dict:
        memory_dict = json.loads(memory)
        sql = f'''
INSERT INTO core_memories (role, key, value)
VALUES ({memory_dict['role']}, {memory_dict['key'], {memory_dict['value']}})
ON CONFLICT(role, key)
DO UPDATE SET
    value = excluded.value,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now');
'''
        return cls.dbn.execute_sql(sql)
    
    @classmethod
    def delete(cls, id: int) -> dict:
        sql = f'''
UPDATE core_memories
SET deleted = 1
WHERE id = {id};
'''
        return cls.dbn.execute_sql(sql)
    
    @classmethod
    def undelete(cls, id: int) -> dict:
        sql = f'''
UPDATE core_memories
SET deleted = 0
WHERE id = {id};
'''
        return cls.dbn.execute_sql(sql)
    
    