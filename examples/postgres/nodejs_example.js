/**
 * PostgreSQL + pgvector の使用例 (Node.js)
 * npm install pg
 */

const { Pool } = require('pg');

// 接続プール作成
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'postgres',
});

async function main() {
  try {
    // 1. 基本的なCRUD操作
    console.log('=== 基本的なCRUD操作 ===');

    // ユーザーを追加
    const insertResult = await pool.query(
      `INSERT INTO users (username, email)
       VALUES ($1, $2)
       ON CONFLICT (username) DO NOTHING
       RETURNING id, username`,
      ['david', 'david@example.com']
    );

    if (insertResult.rows.length > 0) {
      const { id, username } = insertResult.rows[0];
      console.log(`ユーザー作成: ${username} (ID: ${id})`);
    }

    // ユーザー一覧を取得
    const usersResult = await pool.query('SELECT * FROM users');
    console.log(`ユーザー数: ${usersResult.rows.length}`);
    usersResult.rows.forEach(user => {
      console.log(`  - ${user.username} (${user.email})`);
    });

    // 2. ベクトル検索の例
    console.log('\n=== ベクトル検索 ===');

    // サンプルドキュメントを追加
    const generateRandomVector = (dim) => {
      return Array.from({ length: dim }, () => Math.random());
    };

    const documents = [
      {
        title: 'Node.js入門',
        content: 'Node.jsでサーバーサイド開発を学ぶ',
        embedding: generateRandomVector(1536),
      },
      {
        title: 'TypeScript基礎',
        content: 'TypeScriptの型システムを理解する',
        embedding: generateRandomVector(1536),
      },
    ];

    for (const doc of documents) {
      await pool.query(
        `INSERT INTO documents (title, content, embedding, metadata)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT DO NOTHING`,
        [doc.title, doc.content, JSON.stringify(doc.embedding), { category: 'programming' }]
      );
    }

    // クエリベクトル生成
    const queryEmbedding = generateRandomVector(1536);

    // ベクトル類似度検索
    const searchResult = await pool.query(
      `SELECT id, title, content,
              1 - (embedding <=> $1::vector) as similarity
       FROM documents
       WHERE embedding IS NOT NULL
       ORDER BY embedding <=> $1::vector
       LIMIT 3`,
      [JSON.stringify(queryEmbedding)]
    );

    console.log('類似ドキュメント:');
    searchResult.rows.forEach(doc => {
      console.log(`  - ${doc.title} (類似度: ${doc.similarity.toFixed(4)})`);
    });

  } catch (error) {
    console.error('エラー:', error);
  } finally {
    await pool.end();
    console.log('\n接続を閉じました');
  }
}

main();
