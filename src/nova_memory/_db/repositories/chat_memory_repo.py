import json

from ..db.nova_db import NovaDB


class ChatMemoryRepository:
    dbn = NovaDB()

    @classmethod
    def get_messages(cls, conv_id: int) -> dict:
        sql = f'''
SELECT role, content, meta_json FROM messages
WHERE conversation_id = ?
AND evicted = 0;
'''
        params = (conv_id,)
        results = cls.dbn.execute_sql(sql, params, returns_data=True)
        for result in results['data']:
            if result['meta_json'] is not None:
                result['meta_json'] = json.loads(result['meta_json'])
        return results

    @classmethod
    def add_message(cls, conv_id: int, message: dict) -> dict:
        role = message['role']
        if role == 'user' and isinstance(message['content'], dict):
            content = message['content']['text']
            meta_json = json.dumps(message['content']['metadata'])
        else:
            content = message['content']
            meta_json = None

        sql = f'''
INSERT INTO messages (conversation_id, role, content, meta_json)
VALUES (?, ?, ?, ?);
'''
        params = (conv_id, role, content, meta_json)
        return cls.dbn.execute_sql(sql, params)

    @classmethod
    def evict_messages(cls, conv_id: int, count: int) -> dict:
        sql = f'''
UPDATE messages
SET evicted = 1
WHERE id in (
    SELECT id FROM messages
    WHERE conversation_id = ? 
        AND evicted = 0
        AND role != 'system'
    ORDER BY id ASC
    LIMIT ?
);
''' 
        params = (conv_id, count)
        return cls.dbn.execute_sql(sql, params)
